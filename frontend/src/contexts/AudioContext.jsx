import { createContext, useContext, useState, useRef, useCallback } from 'react';
import { api } from '../api';

const AudioContext = createContext(null);

export function AudioProvider({ children }) {
  const [autoReadEnabled, setAutoReadEnabled] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null); // conversation ID
  const [queue, setQueue] = useState([]); // Array of { conversationId, messageIndex }
  const [audioCache, setAudioCache] = useState({}); // Cache audio blobs by key
  const audioRef = useRef(new Audio());

  // Generate cache key
  const getCacheKey = (conversationId, messageIndex) => `${conversationId}-${messageIndex}`;

  // Fetch and cache audio
  const fetchAudio = useCallback(async (conversationId, messageIndex) => {
    const key = getCacheKey(conversationId, messageIndex);
    if (audioCache[key]) {
      return audioCache[key];
    }

    try {
      const audioBlob = await api.speakResponse(conversationId, messageIndex);
      setAudioCache(prev => ({ ...prev, [key]: audioBlob }));
      return audioBlob;
    } catch (error) {
      console.error('Failed to fetch audio:', error);
      return null;
    }
  }, [audioCache]);

  // Play next item in queue
  const playNext = useCallback(async () => {
    if (queue.length === 0) {
      setIsPlaying(false);
      setCurrentlyPlaying(null);
      return;
    }

    const [next, ...remaining] = queue;
    setQueue(remaining);
    setCurrentlyPlaying(next.conversationId);
    setIsPlaying(true);

    const audioBlob = await fetchAudio(next.conversationId, next.messageIndex);
    if (audioBlob) {
      const audioUrl = URL.createObjectURL(audioBlob);
      audioRef.current.src = audioUrl;
      audioRef.current.onended = () => {
        URL.revokeObjectURL(audioUrl);
        playNext();
      };
      audioRef.current.onerror = () => {
        URL.revokeObjectURL(audioUrl);
        playNext();
      };
      try {
        await audioRef.current.play();
      } catch (e) {
        console.error('Audio playback failed:', e);
        playNext();
      }
    } else {
      playNext();
    }
  }, [queue, fetchAudio]);

  // Add to queue and start playing if not already
  const queueAudio = useCallback((conversationId, messageIndex) => {
    const item = { conversationId, messageIndex };
    setQueue(prev => {
      const newQueue = [...prev, item];
      // If not playing, start playing
      if (!isPlaying) {
        setTimeout(() => playNext(), 0);
      }
      return newQueue;
    });
  }, [isPlaying, playNext]);

  // Play specific response (manual trigger)
  const playResponse = useCallback(async (conversationId, messageIndex) => {
    // Stop current playback
    audioRef.current.pause();
    setQueue([]);

    setCurrentlyPlaying(conversationId);
    setIsPlaying(true);

    const audioBlob = await fetchAudio(conversationId, messageIndex);
    if (audioBlob) {
      const audioUrl = URL.createObjectURL(audioBlob);
      audioRef.current.src = audioUrl;
      audioRef.current.onended = () => {
        URL.revokeObjectURL(audioUrl);
        setIsPlaying(false);
        setCurrentlyPlaying(null);
      };
      try {
        await audioRef.current.play();
      } catch (e) {
        console.error('Audio playback failed:', e);
        setIsPlaying(false);
        setCurrentlyPlaying(null);
      }
    } else {
      setIsPlaying(false);
      setCurrentlyPlaying(null);
    }
  }, [fetchAudio]);

  // Stop playback
  const stopPlayback = useCallback(() => {
    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    setQueue([]);
    setIsPlaying(false);
    setCurrentlyPlaying(null);
  }, []);

  // Toggle auto-read
  const toggleAutoRead = useCallback(() => {
    setAutoReadEnabled(prev => !prev);
  }, []);

  // Get cached audio blob for download
  const getAudioBlob = useCallback(async (conversationId, messageIndex) => {
    return fetchAudio(conversationId, messageIndex);
  }, [fetchAudio]);

  const value = {
    autoReadEnabled,
    toggleAutoRead,
    isPlaying,
    currentlyPlaying,
    queueAudio,
    playResponse,
    stopPlayback,
    getAudioBlob,
  };

  return (
    <AudioContext.Provider value={value}>
      {children}
    </AudioContext.Provider>
  );
}

export function useAudio() {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error('useAudio must be used within an AudioProvider');
  }
  return context;
}
