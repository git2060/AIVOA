// src/components/Chat/AIChatInput.jsx
import React, { useState } from "react";

export default function AIChatInput({ disabled, onSend }) {
  const [text, setText] = useState("");

  const submit = () => {
    if (!text.trim()) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <div style={{display:"flex", gap:8, marginTop:10}}>
      <input value={text} onChange={(e)=>setText(e.target.value)} placeholder="Describe interaction or ask..." style={{flex:1, padding:8, borderRadius:6, border:"1px solid #e6e9ee"}} />
      <button className="small-btn" onClick={submit} disabled={disabled}>Send</button>
    </div>
  );
}
