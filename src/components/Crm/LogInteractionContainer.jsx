// src/components/Crm/LogInteractionContainer.jsx
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import LogInteractionForm from "./LogInteractionForm";
import {
  setField,
  addToList,
  // resetInteraction,
} from "../../redux/interactionsSlice";
import { postInteraction } from "../../services/api";

export default function LogInteractionContainer({ onLogged }) {
  const dispatch = useDispatch();
  const interaction = useSelector((s) => s.interactions.interaction);

  console.log("🟢 FORM RECEIVED interaction:", interaction);


  const handleChange = (field, value) => {
    dispatch(setField({ field, value }));
  };

  const handleAddSample = () => {
    dispatch(addToList({ field: "samples_distributed", item: "" }));
  };

  const handleFinalize = async () => {
    try {
      const resp = await postInteraction(interaction);
      console.log("Logged interaction:", resp.data);
      onLogged && onLogged({ ok: true, id: resp.data?.id });
      alert("Interaction logged successfully.");
    } catch (err) {
      console.error("Failed to log:", err);
      alert("Failed to log interaction.");
    }
  };

  return (
    <div>
      <LogInteractionForm
        interaction={interaction}
        onChange={handleChange}
        onAddSample={handleAddSample}
      />

      <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
        <button className="small-btn" onClick={handleFinalize}>
          Finalize & Log Interaction
        </button>

        {/* ---------- TEST BUTTON (temporary) ---------- */}
        <button
          className="small-btn"
          onClick={() => {
            const sample = {
              hcp_name: "Dr. Test",
              interaction_type: "Meeting",
              interaction_date: new Date().toISOString().slice(0, 10),
              attendees: ["Dr. Test"],
              topics_discussed: ["Sample topic"],
              materials_shared: ["Brochure"],
              samples_distributed: [],
              sentiment: "Positive",
              outcomes: "Test outcome",
            };
            console.log("TEST: dispatching setDraftFromAI", sample);
            // dispatch same action your stream code would dispatch
            dispatch({ type: "interactions/setDraftFromAI", payload: sample });
          }}
        >
          TEST: Fill Form From Sample
        </button>
        {/* ---------- end TEST BUTTON ---------- */}
      </div>
    </div>
  );
}
