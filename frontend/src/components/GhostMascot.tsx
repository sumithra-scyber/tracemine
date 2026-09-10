type GhostExpression = "happy" | "sleepy" | "searching" | "surprised";

interface GhostMascotProps {
  expression?: GhostExpression;
  size?: number;
  className?: string;
}

/**
 * The Footprint ghost mascot, reused across every screen so the character
 * feels consistent rather than a one-off landing page graphic.
 * Bobbing/swaying/blinking come from Tailwind's `animate-*` utilities
 * defined in tailwind.config.js, matching the approved landing page mockup.
 */
export default function GhostMascot({ expression = "happy", size = 100, className = "" }: GhostMascotProps) {
  const eyeShape = () => {
    switch (expression) {
      case "sleepy":
        // Half-closed eyes, drawn as short arcs instead of full ellipses.
        return (
          <>
            <path d="M31 50 Q36 54 41 50" stroke="#04342C" strokeWidth="3" strokeLinecap="round" fill="none" />
            <path d="M59 50 Q64 54 69 50" stroke="#04342C" strokeWidth="3" strokeLinecap="round" fill="none" />
          </>
        );
      case "surprised":
        return (
          <>
            <circle cx="36" cy="50" r="6" fill="#04342C" />
            <circle cx="64" cy="50" r="6" fill="#04342C" />
          </>
        );
      case "searching":
        // Eyes shifted slightly, as if looking around/scanning.
        return (
          <>
            <ellipse className="animate-blink" cx="39" cy="50" rx="5" ry="7" fill="#04342C" />
            <ellipse className="animate-blink" cx="67" cy="50" rx="5" ry="7" fill="#04342C" />
          </>
        );
      case "happy":
      default:
        return (
          <>
            <ellipse className="animate-blink" cx="36" cy="50" rx="5" ry="7" fill="#04342C" />
            <ellipse className="animate-blink" cx="64" cy="50" rx="5" ry="7" fill="#04342C" />
          </>
        );
    }
  };

  const mouth =
    expression === "surprised" ? (
      <ellipse cx="50" cy="70" rx="6" ry="8" fill="#04342C" />
    ) : expression === "sleepy" ? (
      <path d="M44 70 Q50 72 56 70" stroke="#04342C" strokeWidth="3" strokeLinecap="round" fill="none" />
    ) : (
      <path d="M42 68 Q50 74 58 68" stroke="#04342C" strokeWidth="3" strokeLinecap="round" fill="none" />
    );

  return (
    <div className={`inline-block animate-bob ${className}`}>
      <svg
        width={size}
        height={size * 1.1}
        viewBox="0 0 100 110"
        className="animate-sway origin-[50%_20%]"
        role="img"
        aria-label={`Footprint ghost mascot, ${expression}`}
      >
        <path
          d="M50 5C25 5 10 25 10 55V95C10 99 14 101 17 98L27 89L37 98C39.5 100 42.5 100 45 98L50 93L55 98C57.5 100 60.5 100 63 98L73 89L83 98C86 101 90 99 90 95V55C90 25 75 5 50 5Z"
          fill="#5DCAA5"
        />
        {eyeShape()}
        {mouth}
      </svg>
    </div>
  );
}
