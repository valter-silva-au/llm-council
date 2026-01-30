import { useState } from 'react';
import { useAudio } from '../contexts/AudioContext';
import './Artifacts.css';

export default function Artifacts({ conversation }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [downloadingAudio, setDownloadingAudio] = useState(null);
  const { getAudioBlob } = useAudio();

  // Get all assistant messages with stage3 responses
  const artifacts = conversation?.messages
    ?.filter((msg) => msg.role === 'assistant' && msg.stage3?.response)
    ?.map((msg, index) => {
      // Find the corresponding user message (previous message)
      const msgIndex = conversation.messages.indexOf(msg);
      const userMsg = conversation.messages[msgIndex - 1];
      const query = userMsg?.content?.slice(0, 50) + (userMsg?.content?.length > 50 ? '...' : '') || 'Query';

      return {
        id: index + 1,
        query,
        response: msg.stage3.response,
        chairman: msg.stage3.model,
        timestamp: new Date().toISOString(), // Would be better from backend
      };
    }) || [];

  if (artifacts.length === 0) {
    return null;
  }

  const downloadArtifact = (artifact) => {
    const content = `# Council Response #${artifact.id}

**Query:** ${artifact.query}

**Chairman:** ${artifact.chairman}

---

${artifact.response}
`;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `council-response-${artifact.id}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadAudioArtifact = async (artifact) => {
    if (!conversation?.id) return;

    setDownloadingAudio(artifact.id);
    try {
      const audioBlob = await getAudioBlob(conversation.id, artifact.id - 1);
      if (audioBlob) {
        const url = URL.createObjectURL(audioBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `council-response-${artifact.id}.mp3`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to download audio:', error);
    } finally {
      setDownloadingAudio(null);
    }
  };

  const downloadAllArtifacts = () => {
    const content = artifacts.map((artifact, idx) => `# Council Response #${artifact.id}

**Query:** ${artifact.query}

**Chairman:** ${artifact.chairman}

---

${artifact.response}

${idx < artifacts.length - 1 ? '\n---\n\n' : ''}`
    ).join('');

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `council-session-${conversation.id.slice(0, 8)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`artifacts-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="artifacts-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="artifacts-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
          <span>Artifacts ({artifacts.length})</span>
        </div>
        <div className="artifacts-actions">
          {isExpanded && (
            <button
              className="download-all-btn"
              onClick={(e) => {
                e.stopPropagation();
                downloadAllArtifacts();
              }}
              title="Download all artifacts"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download All
            </button>
          )}
          <svg
            className={`expand-icon ${isExpanded ? 'rotated' : ''}`}
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </div>

      {isExpanded && (
        <div className="artifacts-list">
          {artifacts.map((artifact) => (
            <div key={artifact.id} className="artifact-item">
              <div className="artifact-info">
                <span className="artifact-number">#{artifact.id}</span>
                <span className="artifact-query" title={artifact.query}>
                  {artifact.query}
                </span>
              </div>
              <div className="artifact-buttons">
                <button
                  className="artifact-download-btn"
                  onClick={() => downloadArtifact(artifact)}
                  title="Download text (Markdown)"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                </button>
                <button
                  className="artifact-download-btn audio"
                  onClick={() => downloadAudioArtifact(artifact)}
                  disabled={downloadingAudio === artifact.id}
                  title="Download audio (MP3)"
                >
                  {downloadingAudio === artifact.id ? (
                    <span className="mini-spinner"></span>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
