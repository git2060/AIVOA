// src/services/api.js
import axios from "axios";

// ----------------------------------
// API CONFIG
// ----------------------------------
const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// ----------------------------------
// POST Interaction (manual)
// ----------------------------------
export const postInteraction = (payload) =>
  api.post(`http://localhost:8000/api/v1/interactions/log_form`, payload, {
    headers: { "Content-Type": "application/json" },
  });

// ----------------------------------
// HELPERS
// ----------------------------------

/**
 * Detect if a TEXT chunk contains valid structured interaction JSON
 */
function isStructuredData(str) {
  if (!str) return false;

  try {
    const obj = JSON.parse(str);

    // must be object
    if (!obj || typeof obj !== "object") return false;

    // require at least meaningful hcp_name
    if (!obj.hcp_name || obj.hcp_name.trim() === "") return false;

    return true;
  } catch {
    return false;
  }
}

// ----------------------------------
// STREAM: Main Agent SSE handler
// ----------------------------------

/**
 * @function streamAgentChat
 * @description Stream chat + tool + structured JSON from backend (SSE)
 * @param {string} threadId
 * @param {string} message
 * @param {function(string):void} onMessage
 * @param {function(any):void} onToolCall
 * @param {function(string):void} onError
 * @param {function(object):void} onFormData   <-- NEW
 */
export async function streamAgentChat(
  threadId,
  message,
  onMessage,
  onToolCall,
  onError,
  onFormData // IMPORTANT
) {
  const url = `http://localhost:8000/api/v1/agent/chat/stream`;

  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ thread_id: threadId, message }),
    });

    if (!resp.ok) throw new Error(`Agent error ${resp.status}`);

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Split SSE chunks by the "\n\n" delimiter
      const parts = buffer.split("\n\n");
      buffer = parts.pop(); // keep incomplete segment

      for (let raw of parts) {
        const clean = raw.replace(/^data:\s*/, "").trim();
        if (!clean || clean === "[DONE]") continue;

        let chunk;
        try {
          chunk = JSON.parse(clean);
        } catch (e) {
          console.error("Could not parse SSE chunk:", clean);
          continue;
        }

        // -------------------------
        // MAIN EVENT ROUTING
        // -------------------------
        switch (chunk.type) {

          case "TEXT": {
            const text = chunk.content;

            // Structured JSON for the FORM
            if (isStructuredData(text)) {
              const data = JSON.parse(text);

              // STOP empty JSON from overwriting real data
              if (!data.hcp_name || data.hcp_name.trim() === "") {
                console.warn("IGNORING EMPTY STRUCTURED JSON:", data);
                break;
              }

              onFormData && onFormData(data);
              break;
            }

            // Normal chat messages
            onMessage && onMessage(text);
            break;
          }

          case "TOOL_CALL": {
            onToolCall && onToolCall(chunk.tool_calls);
            break;
          }

          case "TOOL_RESULT": {
            onToolCall && onToolCall(chunk.content);
            break;
          }

          case "TOOL_CALL_REQUEST":
            console.log("Tool call started...");
            break;

          case "ERROR":
            onError && onError(chunk.content);
            reader.cancel();
            return;

          default:
            console.warn("Unknown stream event:", chunk.type);
            break;
        }

      }
    }
  } catch (err) {
    console.error("Stream error:", err);
    if (onError) onError(err.message || "Stream failed");
  }
}
