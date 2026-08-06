import {api} from "@/api"

export type StrategySource={
  id:number
  source_type:string
  original_name?:string|null
  source_url?:string|null
  mime_type?:string|null
  status:string
  extracted_strategy?:Record<string,any>|null
  error_message?:string|null
  created_at:string
  analyzed_at?:string|null
}

export async function getStrategySources(){
  return (
    await api.get<StrategySource[]>(
      "/strategy-sources",
    )
  ).data
}

export async function uploadStrategySource(
  file:File,
){
  const form=new FormData()

  form.append(
    "file",
    file,
  )

  return (
    await api.post<StrategySource>(
      "/strategy-sources/upload",
      form,
      {
        headers:{
          "Content-Type":
            "multipart/form-data",
        },
      },
    )
  ).data
}

export async function addStrategyUrl(
  url:string,
){
  return (
    await api.post<StrategySource>(
      "/strategy-sources/url",
      {url},
    )
  ).data
}

export async function analyzeStrategySource(
  id:number,
){
  return (
    await api.post(
      `/strategy-sources/${id}/analyze`,
    )
  ).data
}

export async function saveImportedStrategy(
  id:number,
){
  return (
    await api.post(
      `/strategy-sources/${id}/save-strategy`,
    )
  ).data
}
