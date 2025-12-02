// src/redux/chatSlice.js
import { createSlice } from "@reduxjs/toolkit";
import { v4 as uuidv4 } from "uuid";

const initialState = {
  messages: [],
  threadId: uuidv4(),
  streamingStatus: "idle",
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    appendMessage: (state, action) => {
      const msg = action.payload;

      if (typeof msg.content === "object") {
        msg.content = JSON.stringify(msg.content, null, 2); // Convert to string
      }

      state.messages.push(msg);
    },
    setStreamingStatus(state, action) {
      state.streamingStatus = action.payload;
    },
    setThreadId(state, action) {
      state.threadId = action.payload;
    },
    resetChat(state) {
      state.messages = [];
      state.threadId = uuidv4();
      state.streamingStatus = "idle";
    },
  },
});

export const { appendMessage, setStreamingStatus, setThreadId, resetChat } = chatSlice.actions;
export default chatSlice.reducer;
