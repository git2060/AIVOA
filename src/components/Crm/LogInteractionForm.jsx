// src/components/Crm/LogInteractionForm.jsx
import React from "react";

export default function LogInteractionForm({ interaction, onChange, onAddSample }) {
  console.log("FORM RECEIVED interaction:", interaction);
  // interaction: object
  const handleChange = (field) => (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    onChange(field, value);
  };

  return (
    <div className="card">
      <h2 style={{fontSize:18, fontWeight:700, marginBottom:12}}>Log HCP Interaction</h2>

      <div className="form-row">
        <div className="form-col">
          <label>HCP Name</label>
          <input type="text" value={interaction.hcp_name} onChange={handleChange("hcp_name")} />
        </div>
        <div className="form-col">
          <label>Interaction Type</label>
          <select value={interaction.interaction_type} onChange={handleChange("interaction_type")}>
            <option>Meeting</option>
            <option>Call</option>
            <option>Email</option>
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-col">
          <label>Date</label>
          <input type="date" value={interaction.interaction_date} onChange={handleChange("interaction_date")} />
        </div>
        <div className="form-col">
          <label>Attendees (comma-separated)</label>
          <input type="text" value={interaction.attendees.join(", ")} onChange={(e)=>onChange("attendees", e.target.value.split(",").map(s=>s.trim()).filter(Boolean))} />
        </div>
      </div>

      <div style={{marginBottom:12}}>
        <label>Topics Discussed</label>
        <textarea value={interaction.topics_discussed.join("\n")} onChange={(e)=>onChange("topics_discussed", e.target.value.split("\n").map(s=>s.trim()).filter(Boolean))} />
      </div>

      <div style={{marginBottom:12}}>
        <label>Materials Shared</label>
        <input type="text" value={interaction.materials_shared.join(", ")} onChange={(e)=>onChange("materials_shared", e.target.value.split(",").map(s=>s.trim()).filter(Boolean))} />
      </div>

      <div style={{marginBottom:12}}>
        <label>Samples Distributed</label>
        <input type="text" value={interaction.samples_distributed.join(", ")} onChange={(e)=>onChange("samples_distributed", e.target.value.split(",").map(s=>s.trim()).filter(Boolean))} />
        <div style={{marginTop:8}}>
          <button className="small-btn" type="button" onClick={()=>onAddSample && onAddSample()}>Add Sample</button>
        </div>
      </div>

      <div className="form-row" style={{alignItems:"center"}}>
        <div style={{flex:1}}>
          <label>Observed HCP Sentiment</label>
          <div>
            <label style={{marginRight:12}}><input type="radio" name="sentiment" checked={interaction.sentiment==="Positive"} onChange={()=>onChange("sentiment","Positive")}/> Positive</label>
            <label style={{marginRight:12}}><input type="radio" name="sentiment" checked={interaction.sentiment==="Neutral"} onChange={()=>onChange("sentiment","Neutral")}/> Neutral</label>
            <label><input type="radio" name="sentiment" checked={interaction.sentiment==="Negative"} onChange={()=>onChange("sentiment","Negative")}/> Negative</label>
          </div>
        </div>
      </div>

      <div style={{marginTop:12}}>
        <label>Outcomes</label>
        <textarea value={interaction.outcomes} onChange={(e)=>onChange("outcomes", e.target.value)} />
      </div>

      <div style={{marginTop:12, display:"flex", gap:8}}>
        <button className="small-btn" type="button" onClick={()=>{ /* form-level submit handled by parent */ }}>Finalize & Log Interaction</button>
        <button className="link-btn" type="button">Summarize from Voice Note (consent req.)</button>
      </div>
    </div>
  );
}
