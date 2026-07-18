import axios from "axios"
import type {LoginCredentials,LoginResponse,Trade,TradeListResponse,TradePayload} from "@/types"
export const api=axios.create({baseURL:import.meta.env.VITE_API_BASE_URL||"http://127.0.0.1:8000/api/v1",timeout:15000,headers:{"Content-Type":"application/json"}})
api.interceptors.request.use(c=>{const t=localStorage.getItem("tradepilot_access_token");if(t)c.headers.Authorization=`Bearer ${t}`;return c})
api.interceptors.response.use(r=>r,e=>{if(e.response?.status===401){localStorage.removeItem("tradepilot_access_token");localStorage.removeItem("tradepilot_user");if(location.pathname!=="/login")location.href="/login"}return Promise.reject(e)})
export async function loginUser(c:LoginCredentials):Promise<LoginResponse>{try{const r=await api.post<LoginResponse>("/auth/login",c);const t=r.data.access_token||r.data.token;if(!t)throw new Error("No access token returned");return {...r.data,access_token:t}}catch(e){if(!axios.isAxiosError(e)||e.response?.status!==422)throw e;const f=new URLSearchParams();f.set("username",c.email);f.set("password",c.password);const r=await api.post<LoginResponse>("/auth/login",f,{headers:{"Content-Type":"application/x-www-form-urlencoded"}});const t=r.data.access_token||r.data.token;if(!t)throw new Error("No access token returned");return {...r.data,access_token:t}}}
export const me=async()=>{for(const p of ["/auth/me","/profile/me"]){try{return (await api.get(p)).data}catch(e){if(axios.isAxiosError(e)&&e.response?.status===404)continue;throw e}}return null}
export const dashboard=async()=>(await api.get("/analytics/dashboard")).data
export const analysis=async()=>(await api.get("/analytics/analysis")).data
export const trades=async()=>(await api.get<TradeListResponse>("/trades",{params:{limit:200}})).data
export const addTrade=async(p:TradePayload)=>(await api.post<Trade>("/trades",p)).data
export const editTrade=async(id:number,p:Partial<TradePayload>)=>(await api.patch<Trade>(`/trades/${id}`,p)).data
export const removeTrade=async(id:number)=>{await api.delete(`/trades/${id}`)}
export const reviewTrade=async(id:number)=>(await api.get(`/trades/${id}/review`)).data
export const weekly=async()=>(await api.get("/reports/weekly")).data
export const monthly=async()=>(await api.get("/reports/monthly")).data
export const coach=async(message:string)=>(await api.post("/ai/chat",{message})).data
