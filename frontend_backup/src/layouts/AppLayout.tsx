import { Outlet } from "react-router-dom"
import Sidebar from "@/components/app-shell/Sidebar"
import Topbar from "@/components/app-shell/Topbar"
export default function AppLayout(){return <div className="min-h-screen bg-[#060912] text-slate-100"><Sidebar/><div className="min-h-screen lg:pl-72"><Topbar/><main className="px-4 pb-10 pt-4 sm:px-6 lg:px-8"><Outlet/></main></div></div>}
