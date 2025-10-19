document.addEventListener('DOMContentLoaded', function () {

    let profileBox = document.querySelector('.header .content .profile');

    document.querySelector('#user-btn').onclick = () => {
        profileBox.classList.toggle('active');
    }
});


document.addEventListener('DOMContentLoaded', function () {
  let profileBox = document.querySelector('.header .content .profile');
  document.querySelector('#user-btn').onclick = () => {
    profileBox.classList.toggle('active');
  };

  const sections = document.querySelectorAll(".assessment-section");
  let currentSection = 0;

  function showSection(index) {
    sections.forEach((sec, i) => {
      sec.classList.toggle("active", i === index);
    });
  }

  // Initialize first section
  showSection(currentSection);

  sections.forEach((section, index) => {
    const form = section.querySelector(".assessment-form");
    if (!form) return;

    const selects = form.querySelectorAll("select");
    const nextBtn = form.querySelector(".next-btn");
    const prevBtn = form.querySelector(".prev-btn");

    // Check form validity
    function checkUniqueSelections() {
      const values = Array.from(selects).map(sel => sel.value).filter(v => v !== "");
      const hasDuplicates = new Set(values).size !== values.length;
      nextBtn.disabled = !(values.length === selects.length && !hasDuplicates);
    }

    // Add listener to each select
    selects.forEach(sel => {
      sel.addEventListener("change", checkUniqueSelections);
    });

    // Previous button (if any)
    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        currentSection--;
        showSection(currentSection);
      });
    }

    // Next button
    nextBtn.addEventListener("click", () => {
      if (index < sections.length - 1) {
        currentSection++;
        showSection(currentSection);
      }

      // When reach last section, show part 2 button
      if (currentSection === sections.length - 1) {
        const part2Btn = document.getElementById("part2Btn");
        if (part2Btn) {
          part2Btn.style.display = "inline-block";
        }
      }
    });
  });

  document.getElementById("part2Btn").addEventListener("click", function() {
    window.location.href = "Apart2.html";
  });

});



// ----------------------------------------------Part 2 Script --------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  const questionText = document.getElementById("question-text");
  const choiceA = document.getElementById("choiceA");
  const choiceB = document.getElementById("choiceB");
  const generateBtn = document.getElementById("generateReport");
  const quizContainer = document.querySelector(".quiz-container");

  if (!questionText || !choiceA || !choiceB || !generateBtn) return;

  const p2questions = [
    "I enjoy tasks that involve…",
    "When learning something new, I prefer…",
    "I feel more fulfilled when…",
    "My ideal workplace is…",
    "I’m more motivated by…",
    "I’m most comfortable when…",
    "When working with a team, I often…",
    "I value…",
    "If I face a challenge, I tend to…",
    "In the future, I see myself…"
  ];

  const p2answers = {
    A: [
      "Working with tools and materials",
      "Hands-on practice",
      "Building or installing something real",
      "Outdoor or field-based",
      "Creating impact for the environment",
      "Following clear, practical steps",
      "Taking action and guiding hands-on work",
      "Sustainability and the planet",
      "Fixing it directly with available tools",
      "Helping the world go green"
    ],
    B: [
      "Solving technical or data-related problems",
      "Reading, analyzing, and experimenting mentally",
      "Optimizing a process or figuring out how it works",
      "High-tech, lab, or data environment",
      "Building the next generation of technology",
      "Working on complex systems with multiple layers",
      "Analyzing and suggesting technical improvements",
      "Innovation and technological advancement",
      "Researching and finding the root cause logically",
      "Powering the AI revolution"
    ]
  };

  let current = 0;
  let scoreA = 0;
  let scoreB = 0;
  let animating = false; // Prevent double clicks during animation

  function updateQuestion(direction = "none") {
    // Add a small slide animation
    if (direction !== "none") {
      quizContainer.classList.add(`slide-${direction}-out`);
      animating = true;

      setTimeout(() => {
        questionText.innerHTML = `
          ${p2questions[current]}<br>
          <small>(A) ${p2answers.A[current]}<br>(B) ${p2answers.B[current]}</small>
        `;
        quizContainer.classList.remove(`slide-${direction}-out`);
        quizContainer.classList.add(`slide-${direction}-in`);
      }, 250);

      setTimeout(() => {
        quizContainer.classList.remove(`slide-${direction}-in`);
        animating = false;
      }, 500);
    } else {
      questionText.innerHTML = `
        ${p2questions[current]}<br>
        <small>(A) ${p2answers.A[current]}<br>(B) ${p2answers.B[current]}</small>
      `;
    }
  }

  function recordAnswer(choice, direction) {
    if (animating) return;
    if (choice === "A") scoreA++;
    else scoreB++;

    current++;
    if (current < p2questions.length) updateQuestion(direction);
    else showResult();
  }

  function showResult() {
    questionText.textContent = "You’ve completed Part 2!";
    choiceA.classList.add("hidden");
    choiceB.classList.add("hidden");
    generateBtn.classList.remove("hidden");
  }

  // Button clicks
  choiceA.addEventListener("click", () => recordAnswer("A", "left"));
  choiceB.addEventListener("click", () => recordAnswer("B", "right"));

  // Keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") recordAnswer("A", "left");
    if (e.key === "ArrowRight") recordAnswer("B", "right");
  });

  // Swipe detection (mobile)
  let startX = 0;
  document.addEventListener("touchstart", (e) => (startX = e.touches[0].clientX));
  document.addEventListener("touchend", (e) => {
    const endX = e.changedTouches[0].clientX;
    const diff = endX - startX;
    if (Math.abs(diff) < 50) return;
    if (diff > 0) recordAnswer("B", "right");
    else recordAnswer("A", "left");
  });

  generateBtn.addEventListener("click", () => {
        window.location.href = "report.html";
  });

  // Initialize
  updateQuestion();
});


