(() => {
  const boot = document.getElementById("boot");
  const bootCode = document.getElementById("bootCode");
  let pct = 0;
  const bootTimer = setInterval(() => {
    pct += Math.floor(Math.random() * 9) + 4;
    if (pct >= 100) {
      pct = 100;
      clearInterval(bootTimer);
      setTimeout(() => boot.classList.add("is-done"), 180);
    }
    bootCode.textContent = String(pct).padStart(2, "0");
  }, 90);

  const progress = document.getElementById("scrollProgress");
  const updateScroll = () => {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
  };
  window.addEventListener("scroll", updateScroll, {passive:true});
  updateScroll();

  const cursor = document.getElementById("cursorGlow");
  window.addEventListener("pointermove", (e) => {
    cursor.style.left = e.clientX + "px";
    cursor.style.top = e.clientY + "px";
  }, {passive:true});

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
        observer.unobserve(entry.target);
      }
    });
  }, {threshold:0.14});
  document.querySelectorAll(".reveal").forEach((el, i) => {
    el.style.transitionDelay = Math.min(i * 45, 300) + "ms";
    observer.observe(el);
  });

  document.querySelectorAll(".magnetic").forEach((el) => {
    el.addEventListener("pointermove", (e) => {
      if (window.matchMedia("(pointer:coarse)").matches) return;
      const r = el.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width - 0.5) * 8;
      const y = ((e.clientY - r.top) / r.height - 0.5) * 8;
      el.style.transform = "translate(" + x + "px," + y + "px)";
    });
    el.addEventListener("pointerleave", () => el.style.transform = "");
  });

  document.querySelectorAll(".tilt-card").forEach((card) => {
    card.addEventListener("pointermove", (e) => {
      if (window.matchMedia("(pointer:coarse)").matches) return;
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5;
      const y = (e.clientY - r.top) / r.height - .5;
      card.style.transform = "perspective(1000px) rotateX(" + (-y * 4) + "deg) rotateY(" + (x * 5) + "deg) translateY(-4px)";
    });
    card.addEventListener("pointerleave", () => card.style.transform = "");
  });

  const core = document.getElementById("coreVal");
  const signal = document.getElementById("signalVal");
  let t = 0;
  setInterval(() => {
    t += .18;
    const c = Math.round(69 + Math.sin(t) * 10);
    const s = (97.6 + Math.sin(t * .7) * .7).toFixed(1);
    core.textContent = c + "%";
    signal.textContent = s + "%";
  }, 900);

  const typed = document.getElementById("typedLine");
  const lines = [
    "Next target: FreeRTOS + deeper systems work.",
    "Ship the prototype. Then profile it.",
    "Measure first. Optimize second.",
    "The board is innocent until proven otherwise."
  ];
  let lineIndex = 0, charIndex = 0, deleting = false;
  function typeLoop() {
    const line = lines[lineIndex];
    typed.textContent = deleting ? line.slice(0, charIndex--) : line.slice(0, charIndex++);
    if (!deleting && charIndex > line.length + 8) deleting = true;
    if (deleting && charIndex < 0) {
      deleting = false;
      charIndex = 0;
      lineIndex = (lineIndex + 1) % lines.length;
    }
    setTimeout(typeLoop, deleting ? 28 : 54);
  }
  typeLoop();
})();
