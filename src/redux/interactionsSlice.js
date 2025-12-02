// src/redux/interactionsSlice.js
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  interaction: {
    hcp_name: "",
    interaction_type: "Meeting",
    interaction_date: new Date().toISOString().slice(0, 10),

    attendees: [],           // ✅ Must be array
    topics_discussed: [],    // ✅ Must be array
    materials_shared: [],    // ✅ Must be array
    samples_distributed: [], // ✅ Must be array

    sentiment: "Neutral",
    outcomes: "",
    follow_up_actions: [],
  },
};

const interactionsSlice = createSlice({
  name: "interactions",
  initialState,
  reducers: {
    setField(state, action) {
      const { field, value } = action.payload;
      state.interaction[field] = value;
    },
    addToList(state, action) {
      const { field, item } = action.payload;
      if (!Array.isArray(state.interaction[field])) state.interaction[field] = [];
      state.interaction[field].push(item);
    },
    resetInteraction(state) {
      state.interaction = initialState.interaction;
    },
    setDraftFromAI(state, action) {
      console.log("🔥 REDUX setDraftFromAI CALLED with:", action.payload);
      Object.assign(state.interaction, action.payload);
    }

  },
});

export const { setField, addToList, resetInteraction, setDraftFromAI } = interactionsSlice.actions;
export default interactionsSlice.reducer;
