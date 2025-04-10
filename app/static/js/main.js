import { Chart } from "@/components/ui/chart"
// Main JavaScript file for Family Finance Manager

document.addEventListener("DOMContentLoaded", () => {
  // Initialize tooltips
  initTooltips()

  // Initialize notification badges
  updateNotificationBadges()

  // Add event listeners for interactive elements
  addEventListeners()

  // Initialize charts if they exist
  initCharts()

  // Add fun animations for goal progress
  initGoalAnimations()
})

// Initialize tooltips
function initTooltips() {
  const tooltips = document.querySelectorAll("[data-tooltip]")
  tooltips.forEach((tooltip) => {
    tooltip.addEventListener("mouseenter", function () {
      const tooltipText = this.getAttribute("data-tooltip")
      const tooltipEl = document.createElement("div")
      tooltipEl.className = "tooltip"
      tooltipEl.textContent = tooltipText
      document.body.appendChild(tooltipEl)

      const rect = this.getBoundingClientRect()
      tooltipEl.style.top = `${rect.top - tooltipEl.offsetHeight - 10}px`
      tooltipEl.style.left = `${rect.left + (rect.width / 2) - tooltipEl.offsetWidth / 2}px`
      tooltipEl.style.opacity = "1"
    })

    tooltip.addEventListener("mouseleave", () => {
      const tooltipEl = document.querySelector(".tooltip")
      if (tooltipEl) {
        tooltipEl.remove()
      }
    })
  })
}

// Update notification badges
function updateNotificationBadges() {
  fetch("/api/notifications/?unread_only=true")
    .then((response) => response.json())
    .then((data) => {
      const badge = document.querySelector(".notification-badge")
      if (badge) {
        if (data.length > 0) {
          badge.textContent = data.length
          badge.classList.remove("hidden")
        } else {
          badge.classList.add("hidden")
        }
      }
    })
    .catch((error) => console.error("Error fetching notifications:", error))
}

// Add event listeners
function addEventListeners() {
  // Transaction form
  const transactionForm = document.getElementById("transaction-form")
  if (transactionForm) {
    transactionForm.addEventListener("submit", function (e) {
      e.preventDefault()
      const formData = new FormData(this)

      fetch("/api/transactions/", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          // Show success message
          showAlert("Transaction added successfully!", "success")

          // Reset form
          transactionForm.reset()

          // Refresh transactions list
          fetchTransactions()
        })
        .catch((error) => {
          showAlert("Error adding transaction", "error")
          console.error("Error:", error)
        })
    })
  }

  // Goal contribution form
  const contributionForms = document.querySelectorAll(".contribution-form")
  contributionForms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault()
      const formData = new FormData(this)
      const goalId = this.getAttribute("data-goal-id")

      fetch(`/api/goals/${goalId}/contribute`, {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          // Show success message
          showAlert("Contribution added successfully!", "success")

          // Reset form
          form.reset()

          // Refresh goal progress
          updateGoalProgress(goalId)

          // Show celebration animation if goal completed
          if (data.goal_completed) {
            celebrateGoalCompletion()
          }
        })
        .catch((error) => {
          showAlert("Error adding contribution", "error")
          console.error("Error:", error)
        })
    })
  })

  // Mark notification as read
  const notificationItems = document.querySelectorAll(".notification-item")
  notificationItems.forEach((item) => {
    item.addEventListener("click", function () {
      const notificationId = this.getAttribute("data-notification-id")

      fetch(`/api/notifications/${notificationId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ is_read: true }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Update UI
          this.classList.remove("unread")
          updateNotificationBadges()
        })
        .catch((error) => console.error("Error marking notification as read:", error))
    })
  })
}

// Initialize charts
function initCharts() {
  const expenseChartEl = document.getElementById("expense-chart")
  if (expenseChartEl) {
    fetch("/api/reports/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        start_date: getFirstDayOfMonth(),
        end_date: getLastDayOfMonth(),
        period: "monthly",
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Create chart data
        const chartData = []
        const categories = data.overall.categories

        for (const category in categories) {
          chartData.push({
            category: formatCategoryName(category),
            amount: categories[category],
          })
        }

        // Sort by amount descending
        chartData.sort((a, b) => b.amount - a.amount)

        // Create chart
        const ctx = expenseChartEl.getContext("2d")
        new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: chartData.map((item) => item.category),
            datasets: [
              {
                data: chartData.map((item) => item.amount),
                backgroundColor: [
                  "#4f46e5",
                  "#10b981",
                  "#f59e0b",
                  "#ef4444",
                  "#3b82f6",
                  "#ec4899",
                  "#8b5cf6",
                  "#14b8a6",
                ],
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: "right",
              },
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const label = context.label || ""
                    const value = context.raw || 0
                    return `${label}: $${value.toFixed(2)}`
                  },
                },
              },
            },
          },
        })
      })
      .catch((error) => console.error("Error fetching chart data:", error))
  }
}

// Initialize goal animations
function initGoalAnimations() {
  const goalProgressBars = document.querySelectorAll(".goal-progress-bar")
  goalProgressBars.forEach((bar) => {
    const percentage = Number.parseFloat(bar.getAttribute("data-percentage"))

    // Animate progress bar
    bar.style.width = "0%"
    setTimeout(() => {
      bar.style.transition = "width 1s ease-in-out"
      bar.style.width = `${percentage}%`
    }, 100)

    // Add celebration if goal is almost complete
    if (percentage >= 95 && percentage < 100) {
      bar.classList.add("almost-complete")
    }

    // Add celebration if goal is complete
    if (percentage >= 100) {
      celebrateGoalCompletion()
    }
  })
}

// Celebrate goal completion
function celebrateGoalCompletion() {
  // Create confetti effect
  for (let i = 0; i < 100; i++) {
    createConfettiParticle()
  }

  // Show celebration message
  showAlert("🎉 Goal completed! Congratulations! 🎉", "success", 5000)

  // Play celebration sound
  const audio = new Audio("/static/sounds/celebration.mp3")
  audio.play().catch((e) => console.log("Audio play failed:", e))
}

// Create confetti particle
function createConfettiParticle() {
  const confetti = document.createElement("div")
  confetti.className = "confetti"

  // Random position, color and delay
  confetti.style.left = `${Math.random() * 100}vw`
  confetti.style.backgroundColor = getRandomColor()
  confetti.style.animationDelay = `${Math.random() * 3}s`

  document.body.appendChild(confetti)

  // Remove after animation completes
  setTimeout(() => {
    confetti.remove()
  }, 5000)
}

// Get random color
function getRandomColor() {
  const colors = ["#4f46e5", "#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#ec4899", "#8b5cf6", "#14b8a6"]
  return colors[Math.floor(Math.random() * colors.length)]
}

// Show alert message
function showAlert(message, type = "info", duration = 3000) {
  const alertEl = document.createElement("div")
  alertEl.className = `alert alert-${type}`
  alertEl.textContent = message

  document.body.appendChild(alertEl)

  // Show alert
  setTimeout(() => {
    alertEl.classList.add("show")
  }, 10)

  // Hide and remove alert
  setTimeout(() => {
    alertEl.classList.remove("show")
    setTimeout(() => {
      alertEl.remove()
    }, 300)
  }, duration)
}

// Helper functions
function getFirstDayOfMonth() {
  const date = new Date()
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, "0")}-01`
}

function getLastDayOfMonth() {
  const date = new Date()
  const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, "0")}-${lastDay}`
}

function formatCategoryName(category) {
  return category.charAt(0).toUpperCase() + category.slice(1).replace("_", " ")
}

function fetchTransactions() {
  const transactionsList = document.getElementById("transactions-list")
  if (transactionsList) {
    fetch("/api/transactions/")
      .then((response) => response.json())
      .then((data) => {
        // Clear current list
        transactionsList.innerHTML = ""

        // Add transactions
        data.forEach((transaction) => {
          const item = document.createElement("div")
          item.className = "transaction-item"

          const typeClass = transaction.type === "income" ? "income" : "expense"

          item.innerHTML = `
            <div class="transaction-info">
              <div class="transaction-description">${transaction.description}</div>
              <div class="transaction-date">${formatDate(transaction.date)}</div>
            </div>
            <div class="transaction-amount ${typeClass}">
              ${transaction.type === "income" ? "+" : "-"}$${transaction.amount.toFixed(2)}
            </div>
          `

          transactionsList.appendChild(item)
        })
      })
      .catch((error) => console.error("Error fetching transactions:", error))
  }
}

function updateGoalProgress(goalId) {
  fetch(`/api/goals/${goalId}`)
    .then((response) => response.json())
    .then((data) => {
      const progressBar = document.querySelector(`.goal-progress-bar[data-goal-id="${goalId}"]`)
      const progressText = document.querySelector(`.goal-progress-text[data-goal-id="${goalId}"]`)

      if (progressBar && progressText) {
        const percentage = (data.current_amount / data.target_amount) * 100

        // Update progress bar
        progressBar.style.width = `${percentage}%`

        // Update text
        progressText.textContent = `$${data.current_amount.toFixed(2)} of $${data.target_amount.toFixed(2)} (${percentage.toFixed(1)}%)`

        // Update color based on progress
        if (percentage >= 100) {
          progressBar.className = "goal-progress-bar bg-success"
        } else if (percentage >= 70) {
          progressBar.className = "goal-progress-bar bg-info"
        } else if (percentage >= 30) {
          progressBar.className = "goal-progress-bar bg-warning"
        } else {
          progressBar.className = "goal-progress-bar bg-danger"
        }
      }
    })
    .catch((error) => console.error("Error updating goal progress:", error))
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}
