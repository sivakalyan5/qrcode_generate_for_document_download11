document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("document");
  const fileLabel = document.getElementById("file-label");
  if (fileInput && fileLabel) {
    fileInput.addEventListener("change", () => {
      fileLabel.textContent = fileInput.files.length ? fileInput.files[0].name : "Choose a file or tap to browse";
    });
  }
  const copyButton = document.getElementById("copy-link");
  const url = document.getElementById("download-url");
  if (copyButton && url) {
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(url.textContent.trim());
        copyButton.textContent = "Copied!";
        setTimeout(() => copyButton.textContent = "Copy", 1600);
      } catch {
        copyButton.textContent = "Copy unavailable";
      }
    });
  }
});
