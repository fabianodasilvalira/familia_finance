import { Chart } from "@/components/ui/chart"
// Charts for Family Finance Manager

// Initialize charts when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  initExpenseChart()
  initIncomeChart()
  initBudgetChart()
  initTrendsChart()
})

// Initialize expense breakdown chart
function initExpenseChart() {
  const expenseChartEl = document.getElementById("expense-chart")
  if (!expenseChartEl) return

  // Get current date
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1

  // Get first and last day of month
  const firstDay = `${year}-${month.toString().padStart(2, "0")}-01`
  const lastDay = new Date(year, month, 0).getDate()
  const lastDayFormatted = `${year}-${month.toString().padStart(2, "0")}-${lastDay}`

  // Fetch expense data
  fetch("/api/reports/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start_date: firstDay,
      end_date: lastDayFormatted,
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
              backgroundColor: ["#4f46e5", "#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#ec4899", "#8b5cf6", "#14b8a6"],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "right",
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.label || ""
                  const value = context.raw || 0
                  const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: $${value.toFixed(2)} (${percentage}%)`
                },
              },
            },
            title: {
              display: true,
              text: "Expense Breakdown",
            },
          },
        },
      })
    })
    .catch((error) => console.error("Error fetching expense chart data:", error))
}

// Initialize income chart
function initIncomeChart() {
  const incomeChartEl = document.getElementById("income-chart")
  if (!incomeChartEl) return

  // Get last 6 months
  const months = []
  const now = new Date()

  for (let i = 5; i >= 0; i--) {
    const month = new Date(now.getFullYear(), now.getMonth() - i, 1)
    months.push(month)
  }

  // Fetch income data for each month
  Promise.all(
    months.map((month) => {
      const year = month.getFullYear()
      const monthNum = month.getMonth() + 1

      const firstDay = `${year}-${monthNum.toString().padStart(2, "0")}-01`
      const lastDay = new Date(year, monthNum, 0).getDate()
      const lastDayFormatted = `${year}-${monthNum.toString().padStart(2, "0")}-${lastDay}`

      return fetch("/api/reports/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          start_date: firstDay,
          end_date: lastDayFormatted,
          period: "monthly",
        }),
      }).then((response) => response.json())
    }),
  )
    .then((results) => {
      // Extract income data
      const incomeData = results.map((result) => result.overall.total_income)
      const expenseData = results.map((result) => result.overall.total_expenses)

      // Format month labels
      const labels = months.map((month) => {
        return month.toLocaleDateString("en-US", { month: "short", year: "numeric" })
      })

      // Create chart
      const ctx = incomeChartEl.getContext("2d")
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Income",
              data: incomeData,
              backgroundColor: "#10b981",
              borderColor: "#059669",
              borderWidth: 1,
            },
            {
              label: "Expenses",
              data: expenseData,
              backgroundColor: "#ef4444",
              borderColor: "#dc2626",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: (value) => "$" + value,
              },
            },
          },
          plugins: {
            title: {
              display: true,
              text: "Income vs Expenses (Last 6 Months)",
            },
          },
        },
      })
    })
    .catch((error) => console.error("Error fetching income chart data:", error))
}

// Initialize budget chart
function initBudgetChart() {
  const budgetChartEl = document.getElementById("budget-chart")
  if (!budgetChartEl) return

  // Get current month data
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1

  const firstDay = `${year}-${month.toString().padStart(2, "0")}-01`
  const lastDay = new Date(year, month, 0).getDate()
  const lastDayFormatted = `${year}-${month.toString().padStart(2, "0")}-${lastDay}`

  fetch("/api/reports/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start_date: firstDay,
      end_date: lastDayFormatted,
      period: "monthly",
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      const income = data.overall.total_income
      const expenses = data.overall.total_expenses
      const remaining = income - expenses

      // Create chart
      const ctx = budgetChartEl.getContext("2d")
      new Chart(ctx, {
        type: "pie",
        data: {
          labels: ["Spent", "Remaining"],
          datasets: [
            {
              data: [expenses, remaining > 0 ? remaining : 0],
              backgroundColor: ["#ef4444", "#10b981"],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.label || ""
                  const value = context.raw || 0
                  const total = income
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: $${value.toFixed(2)} (${percentage}%)`
                },
              },
            },
            title: {
              display: true,
              text: "Monthly Budget Usage",
            },
          },
        },
      })

      // Update budget summary
      const budgetSummary = document.getElementById("budget-summary")
      if (budgetSummary) {
        const percentUsed = ((expenses / income) * 100).toFixed(1)
        let statusClass = "text-success"

        if (percentUsed >= 90) {
          statusClass = "text-danger"
        } else if (percentUsed >= 70) {
          statusClass = "text-warning"
        }

        budgetSummary.innerHTML = `
          <div class="budget-total">Total Budget: <strong>$${income.toFixed(2)}</strong></div>
          <div class="budget-spent">Spent: <strong>$${expenses.toFixed(2)}</strong></div>
          <div class="budget-remaining">Remaining: <strong>$${remaining.toFixed(2)}</strong></div>
          <div class="budget-percentage ${statusClass}">
            <strong>${percentUsed}%</strong> of budget used
          </div>
        `
      }
    })
    .catch((error) => console.error("Error fetching budget chart data:", error))
}

// Initialize trends chart
function initTrendsChart() {
  const trendsChartEl = document.getElementById("trends-chart")
  if (!trendsChartEl) return

  // Get last 30 days
  const now = new Date()
  const thirtyDaysAgo = new Date(now)
  thirtyDaysAgo.setDate(now.getDate() - 30)

  const startDate = formatDateString(thirtyDaysAgo)
  const endDate = formatDateString(now)

  fetch("/api/reports/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start_date: startDate,
      end_date: endDate,
      period: "daily",
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Extract daily data
      const dailyData = data.by_period

      // Create datasets
      const labels = dailyData.map((day) => {
        const date = new Date(day.period)
        return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
      })

      const expenseData = dailyData.map((day) => day.total_expenses)

      // Calculate 7-day moving average
      const movingAvgData = []
      for (let i = 0; i < expenseData.length; i++) {
        if (i < 6) {
          movingAvgData.push(null)
        } else {
          const sum = expenseData.slice(i - 6, i + 1).reduce((a, b) => a + b, 0)
          movingAvgData.push(sum / 7)
        }
      }

      // Create chart
      const ctx = trendsChartEl.getContext("2d")
      new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Daily Expenses",
              data: expenseData,
              backgroundColor: "rgba(239, 68, 68, 0.2)",
              borderColor: "#ef4444",
              borderWidth: 1,
              pointRadius: 2,
            },
            {
              label: "7-Day Average",
              data: movingAvgData,
              borderColor: "#3b82f6",
              borderWidth: 2,
              pointRadius: 0,
              fill: false,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: (value) => "$" + value,
              },
            },
          },
          plugins: {
            title: {
              display: true,
              text: "Daily Expense Trends (Last 30 Days)",
            },
          },
        },
      })
    })
    .catch((error) => console.error("Error fetching trends chart data:", error))
}

// Helper functions
function formatCategoryName(category) {
  return category.charAt(0).toUpperCase() + category.slice(1).replace("_", " ")
}

function formatDateString(date) {
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, "0")
  const day = date.getDate().toString().padStart(2, "0")
  return `${year}-${month}-${day}`
}
