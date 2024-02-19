const results = getJSONScript("results-data");
console.log(results);

results.forEach(function (value) {
  const group = value[0];
  const data = value[1];

  Object.values(data.results_by_part).map(function (partValue) {
    const part = partValue.part;
    const partData = partValue.average_results;
    const averagePartLabels = partData.map(function (value) {
      return value.item.name;
    });
    const averagePartData = partData.map(function (value) {
      return value.average;
    });
    ctx = document
      .getElementById("chart-average-radar-" + group.id + "-" + part.id)
      .getContext("2d");
    const averageRadarChart = new Chart(ctx, {
      type: "radar",
      data: {
        labels: averagePartLabels,
        datasets: [
          {
            label: group["group_name"],
            data: averagePartData,
            borderColor: themeColor,
            backgroundColor: "rgba(0, 0, 0, 0)",
          },
        ],
      },
      options: {
        scales: {
          r: {
            min: 1,
            max: 5,
            ticks: {
              callback: function (value, index, values) {
                if (data.choices.hasOwnProperty(value)) {
                  return value;
                }
                return "";
              },
            },
          },
        },
      },
    });

    const averageDataSets = [
      {
        label: group["group_name"],
        data: averagePartData,
        borderColor: themeColor,
        tension: 0.1,
      },
    ];

    data.comparison.forEach(function (comparisonData) {
      console.log(comparisonData);
      const comparisonLabel =
        comparisonData.comparison_group.name +
        " / " +
        comparisonData.subject.name;
      const comparisonAverageData = comparisonData.results.map(
        function (value) {
          return value.average;
        },
      );
      const dataset = {
        label: comparisonLabel,
        data: comparisonAverageData,
        borderColor: themeSecondaryColor,
        tension: 0.1,
      };
      averageDataSets.push(dataset);
    });

    ctx = document
      .getElementById("chart-average-" + group.id + "-" + part.id)
      .getContext("2d");
    const averageChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: averagePartLabels,
        datasets: averageDataSets,
      },
      options: {
        scales: {
          y: {
            min: 1,
            max: 5,
            ticks: {
              callback: function (value, index, values) {
                if (data.choices.hasOwnProperty(value)) {
                  return data.choices[value] + " (" + value + ")";
                }
                return "";
              },
            },
          },
        },
      },
    });
  });

  data.frequency.map(function (value) {
    const frequencyLabels = Object.values(value.frequencies).map(
      function (value) {
        return value.label;
      },
    );
    const frequencyData = Object.values(value.frequencies).map(
      function (value) {
        return value.frequency;
      },
    );
    const frequencyBackgroundColors = Object.values(value.frequencies).map(
      function (value) {
        return value["background_color"];
      },
    );
    const frequencyBorderColors = Object.values(value.frequencies).map(
      function (value) {
        return value["border_color"];
      },
    );

    const ctx = document
      .getElementById("chart-frequency-" + group.id + "-" + value.item.id)
      .getContext("2d");
    const frequencyChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: frequencyLabels,
        datasets: [
          {
            label: group["group_name"],
            data: frequencyData,
            borderColor: frequencyBorderColors,
            backgroundColor: frequencyBackgroundColors,
          },
        ],
      },
      options: {
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            title: {
              display: true,
              text: gettext("Number of people"),
            },
            beginAtZero: true,
            ticks: {
              callback: function (value, index, values) {
                if (value % 1 === 0) {
                  return value;
                }
                return "";
              },
            },
          },
        },
      },
    });
  });
});
