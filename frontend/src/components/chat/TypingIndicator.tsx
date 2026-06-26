/** Three blinking dots shown while the assistant "thinks". */
export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-[5px] self-start rounded-[16px_16px_16px_4px] border border-white/[0.08] bg-white/[0.04] px-[18px] py-[14px]">
      {[0, 0.2, 0.4].map((delay) => (
        <span
          key={delay}
          className="h-[6px] w-[6px] animate-blink rounded-full bg-[#9aa3ad]"
          style={{ animationDelay: `${delay}s` }}
        />
      ))}
    </div>
  );
}
