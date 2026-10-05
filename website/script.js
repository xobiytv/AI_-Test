// ===== Sozlamalar =====
const CONFIG = {
  // Tadbir boshlanish vaqti (Toshkent vaqti, UTC+5)
  eventDate: "2026-10-24T15:00:00+05:00",
  // Arizalar yuboriladigan manzil (masalan, Google Apps Script yoki Formspree URL).
  // Bo'sh qolsa, ariza Telegram orqali yuboriladi.
  formEndpoint: "",
  telegramUsername: "biznestown",
};

// ===== Header & mobil menyu =====
const header = document.querySelector(".header");
const nav = document.getElementById("nav");
const burger = document.getElementById("burger");

const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 40);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

burger.addEventListener("click", () => {
  nav.classList.toggle("open");
  burger.classList.toggle("open");
});
nav.querySelectorAll("a").forEach((a) =>
  a.addEventListener("click", () => {
    nav.classList.remove("open");
    burger.classList.remove("open");
  })
);

// ===== Teskari sanoq =====
const cd = Object.fromEntries(
  [...document.querySelectorAll("[data-cd]")].map((el) => [el.dataset.cd, el])
);
const target = new Date(CONFIG.eventDate).getTime();
const pad = (n) => String(n).padStart(2, "0");

function tick() {
  const diff = Math.max(0, target - Date.now());
  const s = Math.floor(diff / 1000);
  cd.d.textContent = pad(Math.floor(s / 86400));
  cd.h.textContent = pad(Math.floor((s % 86400) / 3600));
  cd.m.textContent = pad(Math.floor((s % 3600) / 60));
  cd.s.textContent = pad(s % 60);
  if (diff === 0) {
    document.querySelector("#countdown p").textContent = "Tadbir boshlandi!";
    clearInterval(timer);
  }
}
const timer = setInterval(tick, 1000);
tick();

// ===== Scroll animatsiya =====
const io = new IntersectionObserver(
  (entries) =>
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add("visible");
        io.unobserve(e.target);
      }
    }),
  { threshold: 0.15 }
);
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

// ===== Ro'yxatdan o'tish formasi =====
const form = document.getElementById("regForm");
const msg = document.getElementById("formMsg");

function showMsg(text, ok) {
  msg.textContent = text;
  msg.className = "form__msg " + (ok ? "ok" : "err");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  const phoneDigits = (data.phone || "").replace(/\D/g, "");

  form.querySelector("[name=name]").classList.toggle("invalid", !data.name.trim());
  form.querySelector("[name=phone]").classList.toggle("invalid", phoneDigits.length < 9);
  if (!data.name.trim() || phoneDigits.length < 9) {
    showMsg("Iltimos, ism va telefon raqamingizni to'g'ri kiriting.", false);
    return;
  }

  const btn = form.querySelector("button");
  btn.disabled = true;

  try {
    if (CONFIG.formEndpoint) {
      const res = await fetch(CONFIG.formEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, event: "Tog' Safari", sentAt: new Date().toISOString() }),
      });
      if (!res.ok) throw new Error(res.status);
      showMsg("Rahmat! Arizangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.", true);
    } else {
      const text =
        `Tog' Safari uchun ariza\n` +
        `Ism: ${data.name}\nTelefon: ${data.phone}\n` +
        `Soha: ${data.business || "-"}\nKishilar soni: ${data.count}`;
      window.open(
        `https://t.me/${CONFIG.telegramUsername}?text=${encodeURIComponent(text)}`,
        "_blank",
        "noopener"
      );
      showMsg("Rahmat! Arizani Telegram orqali yuboring — menejerimiz javob beradi.", true);
    }
    form.reset();
  } catch {
    showMsg("Xatolik yuz berdi. Iltimos, telefon orqali bog'laning.", false);
  } finally {
    btn.disabled = false;
  }
});
