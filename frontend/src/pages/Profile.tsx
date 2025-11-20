import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User } from 'lucide-react';
import {
  Button,
  Input,
  Label,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Spinner,
} from '../components/ui';
import api from '../services/api';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export default function Profile() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/users/me');
      setProfile(response.data);
    } catch (err: any) {
      setError('Failed to load profile');
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setUpdating(true);

    try {
      await api.post('/users/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      setSuccess('Password updated successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update password');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    try {
      await api.delete('/users/me');
      localStorage.removeItem('auth_token');
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete account');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Profile Settings</h1>
        <p className="text-[hsl(var(--muted-foreground))] mt-2">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Profile Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Account Information
          </CardTitle>
          <CardDescription>Your account details and status</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {profile && (
            <div className="grid gap-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="font-medium text-[hsl(var(--muted-foreground))]">Username:</div>
                <div className="col-span-2">{profile.username}</div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="font-medium text-[hsl(var(--muted-foreground))]">Email:</div>
                <div className="col-span-2">{profile.email}</div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="font-medium text-[hsl(var(--muted-foreground))]">Status:</div>
                <div className="col-span-2">
                  {profile.is_active ? (
                    <span className="text-green-600 dark:text-green-400">Active</span>
                  ) : (
                    <span className="text-red-600 dark:text-red-400">Inactive</span>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="font-medium text-[hsl(var(--muted-foreground))]">Verified:</div>
                <div className="col-span-2">
                  {profile.is_verified ? (
                    <span className="text-green-600 dark:text-green-400">Verified</span>
                  ) : (
                    <span className="text-yellow-600 dark:text-yellow-400">Not Verified</span>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="font-medium text-[hsl(var(--muted-foreground))]">Member Since:</div>
                <div className="col-span-2">
                  {new Date(profile.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Update your password to keep your account secure</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="current-password">Current Password</Label>
              <Input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Password must be at least 8 characters long
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-new-password">Confirm New Password</Label>
              <Input
                id="confirm-new-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>

            {error && (
              <div className="p-3 text-sm text-[hsl(var(--destructive))] bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/20 rounded-md">
                {error}
              </div>
            )}

            {success && (
              <div className="p-3 text-sm text-green-800 dark:text-green-100 bg-green-100 dark:bg-green-900 border border-green-200 dark:border-green-800 rounded-md">
                {success}
              </div>
            )}

            <Button type="submit" disabled={updating}>
              {updating ? 'Updating...' : 'Update Password'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-[hsl(var(--destructive))]">
        <CardHeader>
          <CardTitle className="text-[hsl(var(--destructive))]">Danger Zone</CardTitle>
          <CardDescription>Irreversible actions for your account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Delete Account</h3>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Permanently delete your account and all associated data
              </p>
            </div>
            <Button variant="destructive" onClick={handleDeleteAccount}>
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
