/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface PodcastItem {
  name: string;
  id: string;
}
export interface PodcastResponse {
  podcasts: PodcastItem[];
}
export interface PromptItem {
  name: string;
  id: string;
}
export interface PromptRequest {
  topic: string;
}
export interface PromptResponse {
  prompts: PromptItem[];
}
export interface ScriptItem {
  name: string;
  id: string;
}
export interface ScriptRequest {
  prompt: string;
}
export interface ScriptResponse {
  scripts: ScriptItem[];
}
export interface Voice {
  voice_id: string;
  name: string;
  category: string;
  labels: VoiceLabel;
}
export interface VoiceLabel {
  accent: string;
  description: string;
  age: string;
  gender: string;
  use_case: string;
}
export interface VoiceResponse {
  voices: Voice[];
}
