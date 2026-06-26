/** Dashboard warning-light vision API. */
import type { Car, Citation } from '@/types';
import { apiPostForm } from './client';

export interface DashboardResult {
  identification: string;
  text: string;
  citations?: Citation[] | null;
}

export function analyzeDashboard(car: Car, file: File): Promise<DashboardResult> {
  const form = new FormData();
  form.append('make', car.make);
  form.append('model', car.model);
  form.append('year', car.year);
  form.append('file', file);
  return apiPostForm<DashboardResult>('/vision/dashboard', form);
}
