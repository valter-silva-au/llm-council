import { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { api } from '../api';
import './Stage3.css';

export default function Stage3({ finalResponse, conversationId }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  if (!finalResponse) {
    return null;
  }

  const handleReadAloud = async () => {
    if (!conversationId) return;

    // If already playing, stop
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const audioBlob = await api.speakResponse(conversationId);
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (err) {
      setError('Failed to synthesize speech. Check AWS credentials.');
      console.error('Speech synthesis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  return (
    <div className="stage stage3">
      <h3 className="stage-title">Stage 3: Final Council Answer</h3>
      <div className="final-response">
        <div className="chairman-header">
          <div className="chairman-label">
            Chairman: {finalResponse.model.split('/')[1] || finalResponse.model}
          </div>
          <button
            className={`read-aloud-btn ${isPlaying ? 'playing' : ''}`}
            onClick={handleReadAloud}
            disabled={isLoading}
            title={isPlaying ? 'Stop' : 'Read Aloud'}
          >
            {isLoading ? 'Loading...' : isPlaying ? 'Stop' : 'Read Aloud'}
          </button>
        </div>
        {error && <div className="speech-error">{error}</div>}
        <div className="final-text markdown-content">
          <ReactMarkdown>{finalResponse.response}</ReactMarkdown>
        </div>
        <audio ref={audioRef} onEnded={handleAudioEnded} style={{ display: 'none' }} />
      </div>
    </div>
  );
}
