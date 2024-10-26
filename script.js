document.getElementById('expense-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const name = document.getElementById('expense-name').value;
    const amount = document.getElementById('expense-amount').value;
    const category = document.getElementById('expense-category').value;

    fetch('/add_expense', {
        method: 'POST',
        body: new URLSearchParams({
            'name': name,
            'amount': amount,
            'category': category
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadExpenses();
        }
    });
});

function loadExpenses() {
    fetch('/api/expenses')
        .then(response => response.json())
        .then(expenses => {
            const expenseList = document.getElementById('expense-list');
            expenseList.innerHTML = '';
            let categoryTotals = {};

            expenses.forEach(expense => {
                const li = document.createElement('li');
                li.innerHTML = `${expense.name}: ₹${expense.amount} (${expense.category}) 
                <button onclick="deleteExpense(${expense.id})">Delete</button>`;
                expenseList.appendChild(li);

                // Calculate category totals for pie chart
                if (!categoryTotals[expense.category]) {
                    categoryTotals[expense.category] = 0;
                }
                categoryTotals[expense.category] += expense.amount;
            });

            drawPieChart(categoryTotals);
        });
}

function deleteExpense(id) {
    fetch(`/delete_expense/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadExpenses();
            }
        });
}

function drawPieChart(data) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    const labels = Object.keys(data);
    const values = Object.values(data);

    if (window.pieChart) {
        window.pieChart.destroy();
    }

    window.pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Expense Categories',
                data: values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}

function logout() {
    fetch('/logout').then(() => {
        window.location.href = '/';
    });
}

// Load expenses when the page loads
window.onload = loadExpenses;
