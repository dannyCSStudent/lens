import { ConfidenceState } from '@repo/contracts';

export function computeConfidenceState(
  supportsCount: number,
  contradictsCount: number
): ConfidenceState {
  if (supportsCount === 0 && contradictsCount === 0) {
    return ConfidenceState.NO_REVIEW;
  }
  if (supportsCount > 0 && contradictsCount > 0) {
    return ConfidenceState.CONFLICTING_EVIDENCE;
  }
  return ConfidenceState.COMMUNITY_REVIEWED;
}
