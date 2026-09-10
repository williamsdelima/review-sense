(() => {
  const API_BASE_URL = "https://review-sense-wr79.onrender.com/api/v1";
  const form = document.querySelector("#summary-form");
  if (!form) return;

  const input = document.querySelector("#article-url");
  const button = document.querySelector("#submit-button");
  const defaultLabel = button.querySelector(".button__default");
  const loadingLabel = button.querySelector(".button__loading");
  const error = document.querySelector("#form-error");
  const result = document.querySelector("#result");
  const title = document.querySelector("#result-title");
  const summary = document.querySelector("#result-summary");
  const takeaways = document.querySelector("#takeaways");
  const readingTime = document.querySelector("#reading-time");
  const languageButtons = document.querySelectorAll("[data-language]");
  let currentLanguage = "en";

  const setLoading = (loading) => {
    button.disabled = loading;
    defaultLabel.hidden = loading;
    loadingLabel.hidden = !loading;
  };
  const showError = (message) => {
    error.textContent = message;
    error.hidden = false;
  };
  const clearError = () => {
    error.textContent = "";
    error.hidden = true;
  };
  const renderResult = (data) => {
    title.textContent = data.title;
    summary.textContent = data.summary;
    readingTime.textContent = data.estimated_reading_time || "";
    takeaways.replaceChildren(
      ...(data.key_takeaways || []).map((item) => {
        const entry = document.createElement("li");
        entry.textContent = item;
        return entry;
      }),
    );
    result.hidden = false;
    languageButtons.forEach((item) =>
      item.classList.toggle(
        "is-active",
        item.dataset.language === currentLanguage,
      ),
    );
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  const request = async (path, body) => {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok)
      throw new Error(
        data.detail || "Não foi possível processar este link. Tente novamente.",
      );
    return data;
  };
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();
    if (!input.checkValidity()) {
      input.reportValidity();
      return;
    }
    setLoading(true);
    try {
      currentLanguage = "en";
      renderResult(await request("/summarize", { url: input.value.trim() }));
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });
  languageButtons.forEach((languageButton) =>
    languageButton.addEventListener("click", async () => {
      const targetLanguage = languageButton.dataset.language;
      if (targetLanguage === currentLanguage || !input.value) return;
      clearError();
      setLoading(true);
      try {
        currentLanguage = targetLanguage;
        renderResult(
          await request("/translate", {
            url: input.value.trim(),
            target_language: targetLanguage,
          }),
        );
      } catch (err) {
        currentLanguage = "en";
        showError(err.message);
      } finally {
        setLoading(false);
      }
    }),
  );
})();
