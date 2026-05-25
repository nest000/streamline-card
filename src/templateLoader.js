import evaluateYaml from "./evaluateYaml";

let remoteTemplates = {};
let isTemplateLoaded = null;

let wsTemplates = {};
let wsTemplatesLoaded = false;

export const getRemoteTemplates = () => remoteTemplates;
export const getIsTemplateLoaded = () => isTemplateLoaded;
export const getWSTemplates = () => wsTemplates;

export const loadWSTemplates = async (hass) => {
  if (wsTemplatesLoaded) { return null; }
  if (!hass?.connection) { return null; }

  try {
    const result = await hass.connection.sendMessagePromise({
      type: "streamline_card/templates",
    });

    wsTemplatesLoaded = true;

    if (result?.templates) {
      wsTemplates = result.templates;
      return wsTemplates;
    }
  } catch (err) {
    wsTemplatesLoaded = true;
    // eslint-disable-next-line no-console
    console.warn(
      "[Streamline Card] Could not load templates from configuration.yaml:",
      err.message,
    );
  }

  return null;
};

const fetchRemoteTemplates = async (url) => {
  const res = await fetch(`${url}?t=${new Date().getTime()}`);
  if (res.ok === false) {
    throw new Error('not found');
  }

  const text = await res.text();

  remoteTemplates = evaluateYaml(text);
  isTemplateLoaded = true;

  return isTemplateLoaded;
};

export const loadRemoteTemplates = () => {
  const filename = "streamline-card/streamline_templates.yaml";

  if (isTemplateLoaded === null) {
    isTemplateLoaded = fetchRemoteTemplates(`/hacsfiles/${filename}`)
      .catch(() => fetchRemoteTemplates(`/local/${filename}`))
      .catch(() => fetchRemoteTemplates(`/local/community/${filename}`));
  }

  return isTemplateLoaded;
};
