interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
}

class AuthService {
  private tokens: AuthTokens | null = null;

  login(email: string, password: string): Promise<AuthTokens> {
    // Implementation for login
    return Promise.resolve({
      accessToken: '',
      refreshToken: '',
    });
  }

  logout(): void {
    this.tokens = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  getAccessToken(): string | null {
    return this.tokens?.accessToken || localStorage.getItem('accessToken');
  }

  setTokens(tokens: AuthTokens): void {
    this.tokens = tokens;
    localStorage.setItem('accessToken', tokens.accessToken);
    if (tokens.refreshToken) {
      localStorage.setItem('refreshToken', tokens.refreshToken);
    }
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

export default new AuthService();
