(() => {
  "use strict";

  const STORAGE_KEY = "medeia.library.v1";
  const $ = (selector) => document.querySelector(selector);
  const form = $("#add-form");
  const sourceInput = $("#source-input");
  const titleInput = $("#title-input");
  const categoryInput = $("#category-input");
  const message = $("#form-message");
  const grid = $("#library-grid");
  const empty = $("#empty-state");
  const count = $("#item-count");
  const searchInput = $("#search-input");
  const filterCategory = $("#filter-category");
  let items = loadItems();

  function loadItems() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      return Array.isArray(value) ? value.filter((item) => item && typeof item.url === "string") : [];
    } catch {
      return [];
    }
  }

  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
      return true;
    } catch {
      showMessage("O armazenamento do navegador está cheio ou indisponível. Exporte o JSON para não perder os dados.", true);
      return false;
    }
  }

  function showMessage(text, isError = false) {
    message.textContent = text;
    message.classList.toggle("error", isError);
  }

  function safeUrl(raw) {
    try {
      const url = new URL(raw.trim());
      if (!["http:", "https:"].includes(url.protocol)) return null;
      return url;
    } catch {
      return null;
    }
  }

  function driveId(url) {
    const match = url.pathname.match(/\/file\/d\/([^/]+)/) ||
      url.pathname.match(/\/document\/d\/([^/]+)/) ||
      url.pathname.match(/\/spreadsheets\/d\/([^/]+)/) ||
      url.pathname.match(/\/presentation\/d\/([^/]+)/);
    return match ? match[1] : url.searchParams.get("id");
  }

  function infer(rawUrl, extinfName = "") {
    const url = safeUrl(rawUrl);
    if (!url) throw new Error("Endereço inválido. Use um link HTTP ou HTTPS.");
    const host = url.hostname.toLowerCase();
    const path = decodeURIComponent(url.pathname).toLowerCase();
    const isDrive = host === "drive.google.com" || host.endsWith(".drive.google.com") || host === "docs.google.com";
    const isPlaylist = /\.(m3u8?|m3u)(?:$)/i.test(path);
    const isHls = /\.m3u8$/i.test(path);
    const extension = (path.match(/\.([a-z0-9]{2,5})$/i) || [,""])[1].toLowerCase();
    let sourceType = "Link";
    let format = extension || "URL";
    let category = "Outros";
    let art = "link";
    let status = "Não verificado";

    if (isDrive) {
      sourceType = "Google Drive";
      format = "Drive";
      category = "Google Drive";
      art = "drive";
      status = driveId(url) ? "Link recebido · acesso não verificado" : "Link recebido · ID não identificado";
    } else if (isPlaylist) {
      sourceType = "Playlist";
      format = isHls ? "M3U8 / HLS" : "M3U";
      category = "Playlists";
      art = "playlist";
      status = "Playlist recebida · fontes não verificadas";
    } else if (["mp4","mkv","avi","mov","webm","mp3","m4v"].includes(extension)) {
      sourceType = "Mídia direta";
      format = extension.toUpperCase();
      status = "Não verificado";
    } else if (/(live|tv|channel|canal|hls)/i.test(path)) {
      sourceType = "Transmissão";
      format = "URL de transmissão";
      category = "TV ao vivo";
      status = "Não verificado";
    }

    const leaf = path.split("/").filter(Boolean).pop() || "";
    const fromPath = leaf.replace(/\.(m3u8?|mp4|mkv|avi|mov|webm|m4v)$/i, "").replace(/[._-]+/g, " ").trim();
    const fallback = isDrive ? "Arquivo do Google Drive" : (fromPath || host);
    return {
      url: url.href,
      sourceType,
      format,
      suggestedCategory: category,
      art,
      status,
      title: (extinfName || fallback).slice(0, 120),
      driveFileId: isDrive ? driveId(url) : null
    };
  }

  function parseM3u(text) {
    const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    const results = [];
    let pendingName = "";
    for (const line of lines) {
      if (line.startsWith("#EXTINF")) {
        const comma = line.lastIndexOf(",");
        pendingName = comma >= 0 ? line.slice(comma + 1).trim() : "";
        if (!pendingName) {
          const tvg = line.match(/tvg-name="([^"]+)"/i);
          pendingName = tvg ? tvg[1] : "";
        }
        continue;
      }
      if (line.startsWith("#")) continue;
      if (/^https?:\/\//i.test(line)) {
        results.push(infer(line, pendingName));
        pendingName = "";
      }
    }
    return results;
  }

  function makeId() {
    return (globalThis.crypto && globalThis.crypto.randomUUID)
      ? globalThis.crypto.randomUUID()
      : "m-" + Date.now() + "-" + Math.random().toString(16).slice(2);
  }

  function addRecord(record, requestedTitle = "", requestedCategory = "Automático") {
    const chosenCategory = requestedCategory === "Automático" ? record.suggestedCategory : requestedCategory;
    items.unshift({
      id: makeId(),
      title: (requestedTitle || record.title || "Conteúdo sem nome").trim().slice(0, 120),
      url: record.url,
      source_type: record.sourceType,
      format: record.format,
      category: chosenCategory,
      availability: "not_checked",
      playback_status: "not_tested",
      validation_note: record.status,
      drive_file_id: record.driveFileId,
      poster: null,
      created_at: new Date().toISOString()
    });
  }

  function render() {
    const query = searchInput.value.trim().toLocaleLowerCase("pt-BR");
    const category = filterCategory.value;
    const visible = items.filter((item) => {
      const text = [item.title, item.url, item.category, item.source_type, item.format].join(" ").toLocaleLowerCase("pt-BR");
      return (!query || text.includes(query)) && (category === "Todas" || item.category === category);
    });
    count.textContent = String(items.length);
    grid.replaceChildren();
    empty.classList.toggle("is-hidden", visible.length > 0);
    if (items.length > 0 && visible.length === 0) {
      empty.classList.remove("is-hidden");
      empty.querySelector("h3").textContent = "Nenhum resultado encontrado";
      empty.querySelector("p").textContent = "Tente outro nome ou remova o filtro selecionado.";
    } else {
      empty.querySelector("h3").textContent = "Sua biblioteca começa aqui";
      empty.querySelector("p").textContent = "Cole um link acima. O MEDEIA vai identificar o formato e criar seu primeiro card.";
    }

    for (const item of visible) {
      const card = document.createElement("article");
      card.className = "media-card";
      const art = document.createElement("div");
      art.className = "card-art" + (item.source_type === "Google Drive" ? " drive" : item.source_type === "Playlist" ? " playlist" : "");
      art.textContent = item.source_type === "Google Drive" ? "▱" : item.source_type === "Playlist" ? "☷" : "▶";
      const artLabel = document.createElement("small");
      artLabel.textContent = "MEDEIA · " + (item.source_type || "LINK").toUpperCase();
      art.append(artLabel);

      const body = document.createElement("div");
      body.className = "card-body";
      const title = document.createElement("div");
      title.className = "card-title";
      title.textContent = item.title;

      const meta = document.createElement("div");
      meta.className = "card-meta";
      for (const label of [item.category, item.format]) {
        const pill = document.createElement("span");
        pill.className = "pill";
        pill.textContent = label || "Não identificado";
        meta.append(pill);
      }
      const status = document.createElement("span");
      status.className = "pill muted";
      status.textContent = item.validation_note || "Não verificado";

      const url = document.createElement("div");
      url.className = "card-url";
      url.textContent = item.url;

      const actions = document.createElement("div");
      actions.className = "card-actions";
      const open = document.createElement("a");
      open.href = item.url;
      open.target = "_blank";
      open.rel = "noopener noreferrer";
      open.textContent = "Abrir link";
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "delete";
      remove.textContent = "Excluir";
      remove.addEventListener("click", () => {
        items = items.filter((entry) => entry.id !== item.id);
        persist();
        render();
      });
      actions.append(open, remove);
      body.append(title, meta, status, url, actions);
      card.append(art, body);
      grid.append(card);
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const raw = sourceInput.value.trim();
    if (!raw) return showMessage("Cole um link ou o conteúdo de uma playlist.", true);
    try {
      let records;
      if (/^#EXTM3U/m.test(raw)) {
        records = parseM3u(raw);
        if (!records.length) throw new Error("Não encontrei endereços HTTP/HTTPS nessa playlist.");
      } else {
        records = [infer(raw)];
      }
      const requestedTitle = titleInput.value.trim();
      const requestedCategory = categoryInput.value;
      records.forEach((record) => addRecord(record, records.length === 1 ? requestedTitle : "", requestedCategory));
      persist();
      render();
      showMessage(records.length === 1 ? "Link adicionado à biblioteca." : records.length + " entradas da playlist adicionadas à biblioteca.");
      sourceInput.value = "";
      titleInput.value = "";
    } catch (error) {
      showMessage(error.message || "Não foi possível interpretar esse endereço.", true);
    }
  });

  $("#clear-form").addEventListener("click", () => { form.reset(); showMessage(""); });
  searchInput.addEventListener("input", render);
  filterCategory.addEventListener("change", render);

  $("#export-json").addEventListener("click", () => {
    const payload = { schema_version: "1.0", catalog: "MEDEIA", generated_at: new Date().toISOString(), items };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "medeia-catalog.json";
    link.click();
    URL.revokeObjectURL(url);
    showMessage("Catálogo JSON exportado.");
  });

  $("#import-json").addEventListener("click", () => $("#import-file").click());
  $("#import-file").addEventListener("change", async (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    try {
      const parsed = JSON.parse(await file.text());
      const incoming = Array.isArray(parsed) ? parsed : parsed.items;
      if (!Array.isArray(incoming)) throw new Error("O JSON não contém uma lista de itens.");
      const known = new Set(items.map((item) => item.url));
      let added = 0;
      for (const item of incoming) {
        if (!item || typeof item.url !== "string" || !safeUrl(item.url) || known.has(item.url)) continue;
        items.push({
          id: item.id || makeId(),
          title: String(item.title || "Conteúdo importado").slice(0, 120),
          url: item.url,
          source_type: item.source_type || "Link importado",
          format: item.format || "Não identificado",
          category: item.category || "Outros",
          availability: item.availability || "not_checked",
          playback_status: item.playback_status || "not_tested",
          validation_note: item.validation_note || "Importado · não verificado",
          drive_file_id: item.drive_file_id || null,
          poster: item.poster || null,
          created_at: item.created_at || new Date().toISOString()
        });
        known.add(item.url);
        added++;
      }
      persist();
      render();
      showMessage(added + " novos registros importados.");
    } catch (error) {
      showMessage(error.message || "Falha ao importar o JSON.", true);
    } finally {
      event.target.value = "";
    }
  });

  render();
})();