window.addEventListener("scroll", function () {
    const hero = document.querySelector(".hero-container");
    if (window.scrollY > 50) {
      hero.classList.add("scrolled");
    } else {
      hero.classList.remove("scrolled");
    }
  });

const scroller = scrollama();

scroller
  .setup({
    step: ".step",
    offset: 0.5,
    debug: false,
  })
  .onStepEnter((response) => {
    if (response.index === 2) {
      drawChart();
    }
  });

function drawChart() {
  const ctx = document.getElementById("tempChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: ["1980", "1990", "2000", "2010", "2020"],
      datasets: [{
        label: "Wassertemperatur (°C)",
        data: [12.3, 12.8, 13.5, 14.1, 14.9],
        borderColor: "blue",
        fill: false
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: false
        }
      }
    }
  });
}