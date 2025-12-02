// src/App.jsx
import React from "react";
import LogInteractionScreen from "./components/Crm/LogInteractionScreen";
import { useDispatch, useSelector } from "react-redux";
import { setField, resetInteraction } from "./redux/interactionsSlice";
import { postInteraction } from "./services/api";
import { appendMessage } from "./redux/chatSlice";

export default function App() {
  const dispatch = useDispatch();
  const interactions = useSelector((s) => s.interactions.interaction);
  const chat = useSelector((s) => s.chat);

  const handlers = {
    onChange: (field, value) => {
      dispatch(setField({ field, value }));
    },
    onAddSample: () => {
      // simple add placeholder
      dispatch(setField({ field:"samples_distributed", value: [...interactions.samples_distributed, "sampleX"]}));
    },
    threadId: chat.threadId,
    sendChatMessage: (msg) => {
      dispatch(appendMessage({ role:"user", content: msg }));
    },
    onSubmit: async (interactionData) => {
      try {
        const resp = await postInteraction(interactionData);
        dispatch(appendMessage({ role:"ai", content: "Interaction logged successfully." }));
        dispatch(resetInteraction());
      } catch (e) {
        dispatch(appendMessage({ role:"ai", content: `Log failed: ${e.message}` }));
      }
    }
  };

  return <LogInteractionScreen interaction={interactions} handlers={handlers} />;
}
