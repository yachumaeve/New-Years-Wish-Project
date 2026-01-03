export interface WishItem {
  recipient_id: number;
  recipient_name: string;
  age: number;
  gender: string;
  wish: string;
  content: string;
  organization: string;
  organization_location: string;
  is_taken_on: number; // 0: 尚未認領, 1: 已認領
}

export interface DonorPayload {
  donor_name: string;
  contact_phone: string;
  email: string;
  recipient_id: number;
}