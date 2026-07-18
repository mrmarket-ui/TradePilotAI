import {Navigate,Route,Routes} from "react-router-dom"
import {useAuth} from "@/Auth"
import Shell from "@/Shell"
import {Login,Dashboard,Trades,Analytics,DNA,Coach,Reports,Strategy,Partners,Billing,Settings} from "@/pages"
function Protected(){const {isAuthenticated,isLoading}=useAuth();if(isLoading)return <div className="grid min-h-screen place-items-center">Loading...</div>;return isAuthenticated?<Shell/>:<Navigate to="/login" replace/>}
export default function App(){return <Routes><Route path="/login" element={<Login/>}/><Route element={<Protected/>}><Route path="/dashboard" element={<Dashboard/>}/><Route path="/trades" element={<Trades/>}/><Route path="/analytics" element={<Analytics/>}/><Route path="/trader-dna" element={<DNA/>}/><Route path="/coach" element={<Coach/>}/><Route path="/strategy-lab" element={<Strategy/>}/><Route path="/reports" element={<Reports/>}/><Route path="/partners" element={<Partners/>}/><Route path="/billing" element={<Billing/>}/><Route path="/settings" element={<Settings/>}/></Route><Route path="*" element={<Navigate to="/dashboard" replace/>}/></Routes>}
