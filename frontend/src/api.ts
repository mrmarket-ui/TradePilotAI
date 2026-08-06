import axios from "axios"
import type {LoginCredentials,LoginResponse,Trade,TradeListResponse,TradePayload} from "@/types"
export const api=axios.create({baseURL:import.meta.env.VITE_API_BASE_URL||"http://127.0.0.1:8000/api/v1",timeout:15000,headers:{"Content-Type":"application/json"}})
api.interceptors.request.use(c=>{const t=localStorage.getItem("tradepilot_access_token");if(t)c.headers.Authorization=`Bearer ${t}`;return c})
api.interceptors.response.use(r=>r,e=>{if(e.response?.status===401){localStorage.removeItem("tradepilot_access_token");localStorage.removeItem("tradepilot_user");if(location.pathname!=="/login")location.href="/login"}return Promise.reject(e)})
export async function loginUser(
  c: LoginCredentials,
): Promise<LoginResponse> {
  const form = new URLSearchParams()

  form.set("username", c.email.trim().toLowerCase())
  form.set("password", c.password)

  const response = await api.post<LoginResponse>(
    "/auth/login",
    form,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    },
  )

  const token =
    response.data.access_token ||
    response.data.token

  if (!token) {
    throw new Error(
      "No access token returned",
    )
  }

  return {
    ...response.data,
    access_token: token,
  }
}
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

export const subscriptionPlans=async()=>(
  await api.get("/subscriptions/plans")
).data

export const mySubscription=async()=>(
  await api.get("/subscriptions/me")
).data

export const createPayPalSubscription=async(
  plan:"pro"|"premium"
)=>(
  await api.post(
    "/subscriptions/paypal/create",
    {plan}
  )
).data

export const cancelSubscription=async()=>(
  await api.post(
    "/subscriptions/cancel"
  )
).data

