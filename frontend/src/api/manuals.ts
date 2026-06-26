/** Manual upload API. */
import type { Car } from '@/types';
import { apiPostForm } from './client';

export interface UploadResult {
  name: string;
  meta: string;
  chunk_count: number;
  embedded: boolean;
  greeting: string;
}

export function uploadManual(
  car: Car,
  file: File,
  opts: { name?: string; kind?: string } = {},
): Promise<UploadResult> {
  const form = new FormData();
  form.append('make', car.make);
  form.append('model', car.model);
  form.append('year', car.year);
  form.append('name', opts.name ?? "Owner's Manual");
  form.append('kind', opts.kind ?? 'owner');
  form.append('file', file);
  return apiPostForm<UploadResult>('/manuals/upload', form);
}
