// src/components/Crm/LogInteractionScreen.jsx
import React from "react";
import AIChatContainer from "../Chat/AIChatContainer";
import LogInteractionContainer from "./LogInteractionContainer";

import { useSelector } from "react-redux";

export default function LogInteractionScreen({ handlers }) {
  const interaction = useSelector((s) => s.interactions.interaction);

  return (
    <div className="app-wrap">
      <div className="header">AI-First HCP Interaction Module</div>

      <div className="grid">
        <div>
          <LogInteractionContainer />
        </div>

        <div>
          <div className="card">
            <div className="chat-header">AI Assistant — Log Interaction via chat</div>

            <AIChatContainer
              threadId={handlers.threadId}
              onSend={handlers.sendChatMessage}
              onLogInteraction={() => handlers.onSubmit(interaction)}  
            />
          </div>
        </div>
      </div>
    </div>
  );
}

