document.addEventListener("DOMContentLoaded", function () {
  const filterBtn = document.querySelector(".filter-btn");
  const recommendBtn = document.querySelector(".recommend-btn");
  const modal = document.getElementById("filter-results-modal");
  const closeBtn = document.querySelector(".close-btn");
  const sortBySelect = document.getElementById("sort-by");
  const tableBody = document.querySelector(".results-table tbody");
  const modalTitle = document.querySelector(".modal-content h2");

  const minExperienceInput = document.getElementById("min-experience");
  const skillSearchInput = document.getElementById("skill-search");
  const applyFilterBtn = document.getElementById("apply-filter-btn");

  const RECOMMENDATION_SCORE_THRESHOLD = 85;

  function sortTable(criteria) {
    let rows = Array.from(tableBody.querySelectorAll("tr"));
    rows.sort((a, b) => {
      let valA, valB;
      let order = criteria.endsWith("_desc") ? -1 : 1;
      let type = criteria.split("_")[0];

      if (type === "score") {
        valA = parseFloat(a.getAttribute("data-score"));
        valB = parseFloat(b.getAttribute("data-score"));
      }

      let comparison = 0;
      if (valA < valB) comparison = -1;
      if (valA > valB) comparison = 1;

      return comparison * order;
    });

    rows.forEach((row) => tableBody.appendChild(row));
  }

  function applyAdvancedFilter(minScore = 0, minExp = 0, skillQuery = "") {
    const query = skillQuery.toLowerCase().trim();
    let visibleCount = 0;

    tableBody.querySelectorAll("tr").forEach((row) => {
      const score = parseFloat(row.getAttribute("data-score"));
      const experience = parseFloat(row.getAttribute("data-experience"));

      const skillsCell = row.cells[2].textContent.toLowerCase();

      const scoreMatch = score >= minScore;

      const expMatch = experience >= minExp;

      const skillMatch = query === "" || skillsCell.includes(query);

      if (scoreMatch && expMatch && skillMatch) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });

    if (!modalTitle.textContent.includes("Đề xuất")) {
      modalTitle.textContent = `Kết quả Lọc Nâng Cao (${visibleCount} ứng viên)`;
    }
  }

  function openModal(isRecommendation) {
    sortBySelect.value = "score_desc";
    sortTable(sortBySelect.value);

    if (isRecommendation) {
      modalTitle.textContent = "Ứng viên Đề xuất (Điểm cao nhất)";
      minExperienceInput.value = 0;
      skillSearchInput.value = "";
      applyAdvancedFilter(RECOMMENDATION_SCORE_THRESHOLD, 0, "");
    } else {
      modalTitle.textContent = "Kết quả Lọc Nâng Cao & Đánh giá CV";

      const minExp = parseFloat(minExperienceInput.value) || 0;
      const skillQuery = skillSearchInput.value;
      applyAdvancedFilter(0, minExp, skillQuery);
    }
    modal.style.display = "block";
  }

  filterBtn.addEventListener("click", function (event) {
    event.preventDefault();
    openModal(false);
  });

  recommendBtn.addEventListener("click", function (event) {
    event.preventDefault();
    openModal(true);
  });

  applyFilterBtn.addEventListener("click", function () {
    const minExp = parseFloat(minExperienceInput.value) || 0;
    const skillQuery = skillSearchInput.value;
    if (modalTitle.textContent.includes("Đề xuất")) {
      modalTitle.textContent = "Kết quả Lọc Nâng Cao & Đánh giá CV";
    }

    applyAdvancedFilter(0, minExp, skillQuery);
    sortTable(sortBySelect.value);
  });

  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  sortBySelect.addEventListener("change", (e) => {
    sortTable(e.target.value);
    const minExp = parseFloat(minExperienceInput.value) || 0;
    const skillQuery = skillSearchInput.value;

    if (modalTitle.textContent.includes("Đề xuất")) {
      applyAdvancedFilter(RECOMMENDATION_SCORE_THRESHOLD, 0, "");
    } else {
      applyAdvancedFilter(0, minExp, skillQuery);
    }
  });
});
