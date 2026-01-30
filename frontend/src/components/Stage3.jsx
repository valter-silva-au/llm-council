import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { useAudio } from '../contexts/AudioContext';
import { api } from '../api';
import './Stage3.css';

export default function Stage3({ finalResponse, conversationId, messageIndex = 0 }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [hasAutoPlayed, setHasAutoPlayed] = useState(false);
  const { autoReadEnabled, queueAudio, playResponse, isPlaying, currentlyPlaying } = useAudio();

  // Auto-read when stage3 first appears and auto-read is enabled
  useEffect(() => {
    if (autoReadEnabled && finalResponse && !hasAutoPlayed && conversationId) {
      setHasAutoPlayed(true);
      queueAudio(conversationId, messageIndex);
    }
  }, [autoReadEnabled, finalResponse, hasAutoPlayed, conversationId, messageIndex, queueAudio]);

  if (!finalResponse) {
    return null;
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(finalResponse.response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([finalResponse.response], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'council-response.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReadAloud = async () => {
    if (!conversationId) return;

    // If currently playing this response, it will be handled by the context
    setIsLoading(true);
    setError(null);

    try {
      await playResponse(conversationId, messageIndex);
    } catch (err) {
      setError('Failed to synthesize speech.');
      console.error('Speech synthesis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const isCurrentlyPlaying = isPlaying && currentlyPlaying === conversationId;

  return (
    <div className="stage stage3">
      <h3 className="stage-title">Stage 3: Final Council Answer</h3>
      <div className="final-response">
        <div className="chairman-header">
          <div className="chairman-label">
            Chairman: {finalResponse.model.split('/')[1] || finalResponse.model}
          </div>
          <div className="action-buttons">
            <button
              className="action-btn"
              onClick={handleCopy}
              title="Copy to clipboard"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button
              className="action-btn"
              onClick={handleDownload}
              title="Download as Markdown"
            >
              Download
            </button>
            <button
              className={`action-btn read-aloud ${isCurrentlyPlaying ? 'playing' : ''}`}
              onClick={handleReadAloud}
              disabled={isLoading}
              title={isCurrentlyPlaying ? 'Playing...' : 'Read Aloud'}
            >
              {isLoading ? 'Loading...' : isCurrentlyPlaying ? 'Playing...' : 'Read Aloud'}
            </button>
          </div>
        </div>
        {error && <div className="speech-error">{error}</div>}
        <div className="final-text markdown-content">
          <ReactMarkdown>{finalResponse.response}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
