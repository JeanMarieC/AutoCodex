/** Top bar: logo, optional car badge, and the account control. */
interface HeaderProps {
  showCarBadge: boolean;
  carLabel: string;
  onResetCar: () => void;
  email: string | null;
  onLogout: () => void;
  onSignIn: () => void;
}

export default function Header({
  showCarBadge,
  carLabel,
  onResetCar,
  email,
  onLogout,
  onSignIn,
}: HeaderProps) {
  return (
    <div className="mx-auto flex max-w-[880px] items-center justify-between px-[2px] pt-[26px] pb-2">
      <div className="flex items-center gap-[11px]">
        <div className="flex h-[30px] w-[30px] items-center justify-center rounded-lg border border-white/10 bg-gradient-to-br from-[#2a2f37] to-[#0f1115] shadow-[0_0_18px_rgba(111,177,255,0.18)]">
          <div className="h-[13px] w-[13px] rotate-[35deg] rounded-full border-2 border-accent border-t-transparent" />
        </div>
        <span className="font-display text-[13px] font-semibold uppercase tracking-[0.14em] text-[#e7eaee]">
          Manual<span className="text-accent">.ai</span>
        </span>
      </div>

      <div className="flex items-center gap-[10px]">
        {showCarBadge && (
          <div className="flex items-center gap-[10px] rounded-full border border-white/10 bg-white/[0.04] py-[7px] pr-2 pl-[14px] backdrop-blur-[8px]">
            <span className="h-[7px] w-[7px] rounded-full bg-accent shadow-[0_0_8px_#6fb1ff]" />
            <span className="text-[13px] font-semibold">{carLabel}</span>
            <button
              onClick={onResetCar}
              className="ma-chip cursor-pointer rounded-full border-none bg-white/[0.06] px-[11px] py-[5px] text-[11.5px] font-semibold text-[#aeb4bc]"
            >
              Change car
            </button>
          </div>
        )}

        {email ? (
          <div className="flex items-center gap-[10px] rounded-full border border-white/10 bg-white/[0.04] py-[6px] pr-2 pl-[12px]">
            <span className="max-w-[160px] truncate text-[12.5px] text-ink-soft">{email}</span>
            <button
              onClick={onLogout}
              className="ma-chip cursor-pointer rounded-full border-none bg-white/[0.06] px-[10px] py-[5px] text-[11.5px] font-semibold text-[#aeb4bc]"
            >
              Log out
            </button>
          </div>
        ) : (
          <button
            onClick={onSignIn}
            className="ma-chip cursor-pointer rounded-full border border-white/10 bg-white/[0.04] px-[14px] py-[7px] text-[12.5px] font-semibold text-[#aeb4bc]"
          >
            Sign in
          </button>
        )}
      </div>
    </div>
  );
}
