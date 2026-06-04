import type { BiasFinding } from '../types/audit';

type EvidenceTextProps = {
  text: string;
  findings: BiasFinding[];
};

export function EvidenceText({ text, findings }: EvidenceTextProps) {
  const ranges = findings
    .map((finding) => ({ finding, start: finding.position?.[0] ?? -1, end: finding.position?.[1] ?? -1 }))
    .filter((item) => item.start >= 0 && item.end > item.start)
    .sort((a, b) => a.start - b.start);

  if (!ranges.length) {
    return <div className="evidence-text">{text}</div>;
  }

  const nodes = [];
  let cursor = 0;

  for (const range of ranges) {
    if (range.start < cursor) continue;
    if (range.start > cursor) {
      nodes.push(<span key={`plain-${cursor}`}>{text.slice(cursor, range.start)}</span>);
    }
    nodes.push(
      <mark key={`${range.start}-${range.end}`} className={`evidence-mark ${range.finding.level}`} title={range.finding.reason}>
        {text.slice(range.start, range.end)}
      </mark>,
    );
    cursor = range.end;
  }

  if (cursor < text.length) {
    nodes.push(<span key={`plain-${cursor}`}>{text.slice(cursor)}</span>);
  }

  return <div className="evidence-text">{nodes}</div>;
}