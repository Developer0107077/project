// =============================================
//  PyDev Blog — main.js
// =============================================

document.addEventListener('DOMContentLoaded', () => {

  // ---- NAVBAR scroll effect ----
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  // ---- BURGER mobile menu ----
  const burger = document.getElementById('burger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (burger && mobileMenu) {
    burger.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
    });
    // Close on link click
    mobileMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => mobileMenu.classList.remove('open'));
    });
  }

  // ---- FILTER buttons (index page) ----
  const filterBtns = document.querySelectorAll('.filter-btn');
  const listCards = document.querySelectorAll('.list-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      listCards.forEach(card => {
        const cat = card.dataset.category;
        if (filter === 'all' || cat === filter) {
          card.classList.remove('hidden');
          card.style.animation = 'none';
          card.offsetHeight; // reflow
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  // ---- ACCORDION (article detail page) ----
  const toggleBtn = document.getElementById('toggleCodeBtn');
  const wrapper = document.getElementById('codeSnippetWrapper');
  const arrow = document.getElementById('accordionArrow');

  if (toggleBtn && wrapper) {
    toggleBtn.addEventListener('click', () => {
      const isOpen = wrapper.style.maxHeight && wrapper.style.maxHeight !== '0px';
      if (isOpen) {
        wrapper.style.maxHeight = '0px';
        if (arrow) {
          arrow.textContent = "▶ ko'rish";
          arrow.style.color = 'var(--text-muted)';
        }
      } else {
        wrapper.style.maxHeight = wrapper.scrollHeight + 'px';
        if (arrow) {
          arrow.textContent = '▼ yopish';
          arrow.style.color = 'var(--accent-green)';
        }
      }
    });
  }

  // ---- NEWSLETTER (AJAX post) ----
  const nlForm = document.getElementById('nl-form');
  const msg = document.getElementById('nlMessage');
  if (nlForm && msg) {
    nlForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = nlForm.querySelector('input[name="email"]').value;
      const csrf = nlForm.querySelector('[name=csrfmiddlewaretoken]').value;
      msg.textContent = '⏳ Tekshirilmoqda...';
      try {
        const res = await fetch('/newsletter/subscribe/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrf
          },
          body: `email=${encodeURIComponent(email)}`
        });
        const data = await res.json();
        msg.textContent = data.message;
        msg.style.color = data.ok ? 'var(--accent-green)' : 'var(--accent-red)';
        if (data.ok) nlForm.reset();
      } catch {
        msg.textContent = 'Xatolik yuz berdi. Qayta urinib ko\'ring.';
        msg.style.color = 'var(--accent-red)';
      }
    });
  }

  // ---- VOTE SYSTEM (Index & Article Detail) ----
  const voteButtons = document.querySelectorAll(".vote-btn");

  voteButtons.forEach(button => {
    button.addEventListener("click", async function (e) {
      e.preventDefault();

      const voteUrl = this.getAttribute("data-url"); 
      const voteType = this.getAttribute("data-type"); 
      
      const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
      if (!csrfTokenElement) {
        console.error("CSRF token topilmadi!");
        return;
      }
      const csrfToken = csrfTokenElement.value;

      // index.html uchun '.card-votes', article_detail.html uchun '.vote-row' konteynerini aniqlaymiz
      const voteContainer = this.closest(".card-votes") || this.closest(".vote-row");

      try {
        const response = await fetch(voteUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest"
          },
          body: `vote_type=${encodeURIComponent(voteType)}`
        });

        if (!response.ok) throw new Error("Server xatoligi");

        const data = await response.json();

        if (data.ok) {
          // Konteyner ichidagi tegishli sonlarni yangilaymiz
          const likeSpan = voteContainer.querySelector(".like-count") || document.getElementById("like-count");
          const dislikeSpan = voteContainer.querySelector(".dislike-count") || document.getElementById("dislike-count");

          if (likeSpan) likeSpan.textContent = data.likes_count;
          if (dislikeSpan) dislikeSpan.textContent = data.dislikes_count;

          // Faqat shu maqolaga tegishli tugmalardan active klassini o'chiramiz
          const siblingButtons = voteContainer.querySelectorAll(".vote-btn");
          siblingButtons.forEach(btn => btn.classList.remove("active"));

          // Agar foydalanuvchi ovozini butunlay bekor qilmagan bo'lsa (yangi ovoz bergan bo'lsa)
          if (data.user_vote === voteType) {
            this.classList.add("active");
          }
        } else {
          alert(data.error || "Xatolik yuz berdi.");
        }
      } catch (error) {
        console.error("Ovoz berishda xatolik:", error);
      }
    });
  });

});