"use client";

import { useEffect, useRef, useState } from "react";

interface Token {
  id: number;
  text: string;
}

interface Props {
  content: string;
  isStreaming: boolean;
}

export default function StreamingMessage({ content, isStreaming }: Props) {
  const [tokens, setTokens] = useState<Token[]>([]);
  const prevContentRef = useRef("");
  const counterRef = useRef(0);

  useEffect(() => {
    const prev = prevContentRef.current;
    const next = content;

    if (next.length > prev.length) {
      const newText = next.slice(prev.length); // only the new characters
      setTokens((t) => [
        ...t,
        { id: counterRef.current++, text: newText },
      ]);
    } else if (next.length === 0) {
      // Reset on clear
      setTokens([]);
      counterRef.current = 0;
    }

    prevContentRef.current = next;
  }, [content]);

  return (
    <span>
      {tokens.map((token) => (
        <span key={token.id} className="animate-fadein">
          {token.text}
        </span>
      ))}
      {isStreaming && (
        <span className="inline-block w-2 h-3.5 ml-0.5 align-middle bg-zinc-400 animate-pulse rounded-sm" />
      )}
    </span>
  );
}