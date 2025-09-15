export interface User {
  id?: number;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface DataSource {
  id: number;
  name: string;
  type: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Employee {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  position: string;
  hire_date?: string;
  status: string;
  data_source_id: number;
  created_at: string;
  updated_at: string;
}

export interface ETLJob {
  id: number;
  source_id: number;
  file_path: string;
  status: string;
  records_processed?: number;
  records_failed?: number;
  created_at: string;
  error_details?: string;
}

export interface ApiError {
  detail: string;
}