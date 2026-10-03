function parseUtc(isoString: string): Date {
    const hasTZ = /[Zz]|[+-]\d\d:\d\d$/.test(isoString);
    return new Date(hasTZ ? isoString : isoString + "Z");
}

const UNITS: [unit: string, ms: number][] = [
    ["y", 365 * 24 * 60 * 60 * 1000],
    ["mo", 30 * 24 * 60 * 60 * 1000],
    ["d", 24 * 60 * 60 * 1000],
    ["h", 60 * 60 * 1000],
    ["m", 60 * 1000],
];

export function formatDate(createdAt: string): string {
    // input format: 2026-09-23T18:26:43.945755
    const diffMs = Date.now() - parseUtc(createdAt).getTime();

    for (const [unit, unitMs] of UNITS) {
        const count = Math.floor(diffMs / unitMs);
        if (count >= 1) {
            return `${count}${unit} ago`;
        }
    }

    return "just now";
}