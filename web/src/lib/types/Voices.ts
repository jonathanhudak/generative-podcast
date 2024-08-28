// src/types/Voice.ts
export interface FineTuning {
	is_allowed_to_fine_tune: boolean;
	state: Record<string, string>;
	verification_failures: string[]; // Changed from any[] to string[]
	verification_attempts_count: number;
	manual_verification_requested: boolean;
	language: string;
	progress: Record<string, unknown>; // Changed from any to unknown
	message: Record<string, string>; // Changed from any to string
	dataset_duration_seconds: number | null;
	verification_attempts: string | null; // Changed from any to string
	slice_ids: string[] | null; // Changed from any to string[]
	manual_verification: string | null; // Changed from any to string
}

export interface Labels {
	accent: string;
	description: string;
	age: string;
	gender: string;
	use_case: string;
}

export interface Voice {
	voice_id: string;
	name: string;
	samples: string | null; // Changed from any to string
	category: string;
	fine_tuning: FineTuning;
	labels: Labels;
	description: string | null;
	preview_url: string;
	available_for_tiers: string[]; // Changed from any[] to string[]
	settings: Record<string, unknown> | null; // Changed from any to unknown
	sharing: Record<string, unknown> | null; // Changed from any to unknown
	high_quality_base_model_ids: string[];
	safety_control: Record<string, unknown> | null; // Changed from any to unknown
	voice_verification: {
		requires_verification: boolean;
		is_verified: boolean;
		verification_failures: string[]; // Changed from any[] to string[]
		verification_attempts_count: number;
		language: string | null;
		verification_attempts: string | null; // Changed from any to string
	};
	permission_on_resource: Record<string, unknown> | null; // Changed from any to unknown
	is_legacy: boolean;
	is_mixed: boolean;
}

export interface VoicesData {
	voices: Voice[];
}
