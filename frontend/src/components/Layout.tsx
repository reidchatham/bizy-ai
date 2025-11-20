import { Outlet, Link, useNavigate } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, Target, BarChart3, LogOut } from 'lucide-react';

export default function Layout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold">Bizy AI</h1>
            <div className="flex space-x-4">
              <Link to="/" className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent">
                <LayoutDashboard size={18} />
                Dashboard
              </Link>
              <Link to="/tasks" className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent">
                <CheckSquare size={18} />
                Tasks
              </Link>
              <Link to="/goals" className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent">
                <Target size={18} />
                Goals
              </Link>
              <Link to="/analytics" className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent">
                <BarChart3 size={18} />
                Analytics
              </Link>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </nav>
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
