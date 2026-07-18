import {StrictMode} from "react"
import {createRoot} from "react-dom/client"
import {BrowserRouter} from "react-router-dom"
import {QueryClient,QueryClientProvider} from "@tanstack/react-query"
import App from "./App"
import "./index.css"
import {AuthProvider} from "@/Auth"
const client=new QueryClient({defaultOptions:{queries:{retry:1,refetchOnWindowFocus:false}}})
createRoot(document.getElementById("root")!).render(<StrictMode><QueryClientProvider client={client}><BrowserRouter><AuthProvider><App/></AuthProvider></BrowserRouter></QueryClientProvider></StrictMode>)
