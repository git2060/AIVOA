// src/components/Chat/AIChatContainer.jsx
import React, { useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import AIChatInput from "./AIChatInput";
import { appendMessage, setStreamingStatus, setThreadId } from "../../redux/chatSlice";
import { setDraftFromAI } from "../../redux/interactionsSlice";
import { streamAgentChat } from "../../services/api";

export default function AIChatContainer({ threadId, onSend, onLogInteraction }) {
  const dispatch = useDispatch();
  const chat = useSelector((s)=>s.chat);
  const interactions = useSelector((s)=>s.interactions);
  const listRef = useRef();

  useEffect(()=>{
    // if parent provided threadId, ensure store sync (optional)
    if (threadId) dispatch(setThreadId(threadId));
  },[threadId, dispatch]);

  useEffect(()=>{
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  },[chat.messages]);

  const handleMessage = (text) => {
    // local append user message
    dispatch(appendMessage({ role: "user", content: text }));
    dispatch(setStreamingStatus("loading"));

    // stream to backend agent
    streamAgentChat(
      chat.threadId,
      text,
      (aiText)=>{
        dispatch(appendMessage({ role: "ai", content: aiText }));
      },
      (toolCall) => {
        console.log("AIChatContainer received toolCall:", toolCall);

        // Sometimes streamAgentChat sends a string → ignore
        if (!toolCall || typeof toolCall !== "object") return;

        // Normalize: toolCall is already a single object
        const tc = toolCall;

        console.log("AIChatContainer processing tc:", tc);

        if (
          (tc.name === "extract_interaction_from_text" ||
          tc.name === "log_interaction") &&
          tc.args
        ) {
          const data = tc.args.interaction_data || tc.args;

          console.log("Dispatching setDraftFromAI with:", data);
          dispatch(setDraftFromAI(data));
        }
      },


      (err)=>{
        dispatch(appendMessage({ role: "ai", content: `Agent error: ${err}` }));
      }
    );
  };

  return (
    <div>
      <div ref={listRef} className="chat-list" aria-live="polite">
        {chat.messages.map((m, idx)=>(
          <div key={idx} className={`chat-msg ${m.role==="user" ? "user" : "ai"}`}>
            <div style={{fontSize:13, color:"#374151", marginBottom:6}}>{m.role.toUpperCase()}</div>
            <div>{m.content}</div>
          </div>
        ))}
      </div>

      <AIChatInput disabled={chat.streamingStatus==="loading"} onSend={handleMessage} />

      <div className="footer-row" style={{marginTop:10}}>
        <div className="badge">Thread: {chat.threadId}</div>
        <div style={{flex:1}} />
        <button className="small-btn" onClick={()=>onLogInteraction && onLogInteraction(interactions.interaction)}>Log interaction details or ask</button>
      </div>
    </div>
  );
}
