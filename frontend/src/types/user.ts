export interface User {
  id: string;
  email: string;
  username: string;
  fullName: string;
  isActive: boolean;
  isVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}
