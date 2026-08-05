import {
  Plus,
  Trash2,
} from "lucide-react"
import {
  useState,
} from "react"
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  createAdminPartnerOffer,
  disableAdminPartnerOffer,
  getAdminPartnerOffers,
} from "@/api/admin/partnerOffers"
import {
  getAdminPartners,
} from "@/api/admin/partners"

export default function AdminPartnerOffers(){
  const qc=useQueryClient()

  const [open,setOpen]=useState(false)

  const [form,setForm]=useState({
    partner_id:"",
    title:"",
    description:"",
    coupon_code:"",
    offer_url:"",
  })

  const offersQuery=useQuery({
    queryKey:["admin-partner-offers"],
    queryFn:getAdminPartnerOffers,
  })

  const partnersQuery=useQuery({
    queryKey:["admin-partners"],
    queryFn:getAdminPartners,
  })

  const createMutation=useMutation({
    mutationFn:()=>createAdminPartnerOffer({
      partner_id:Number(form.partner_id),
      title:form.title,
      description:form.description||undefined,
      coupon_code:form.coupon_code||undefined,
      offer_url:form.offer_url||undefined,
      active:true,
    }),
    onSuccess:async()=>{
      setOpen(false)
      setForm({
        partner_id:"",
        title:"",
        description:"",
        coupon_code:"",
        offer_url:"",
      })

      await qc.invalidateQueries({
        queryKey:["admin-partner-offers"],
      })
    },
  })

  const disableMutation=useMutation({
    mutationFn:disableAdminPartnerOffer,
    onSuccess:async()=>{
      await qc.invalidateQueries({
        queryKey:["admin-partner-offers"],
      })
    },
  })

  const partnerMap=new Map(
    (partnersQuery.data?.partners||[])
      .map(p=>[p.id,p.name]),
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[.25em] text-blue-300">
            Affiliate Offers
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            Partner Offers
          </h1>
        </div>

        <button
          onClick={()=>setOpen(true)}
          className="flex items-center gap-2 rounded-2xl bg-blue-500 px-5 py-3"
        >
          <Plus className="size-4"/>
          Add Offer
        </button>
      </div>

      <div className="premium-card overflow-x-auto rounded-3xl">
        <table className="w-full min-w-[800px]">
          <thead>
            <tr>
              {[
                "Partner",
                "Title",
                "Coupon",
                "Status",
                "Actions",
              ].map(x=>(
                <th
                  key={x}
                  className="px-5 py-4 text-left text-xs uppercase text-slate-500"
                >
                  {x}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {(offersQuery.data?.offers||[]).map(offer=>(
              <tr
                key={offer.id}
                className="border-t border-white/[.06]"
              >
                <td className="px-5 py-4">
                  {partnerMap.get(offer.partner_id)||offer.partner_id}
                </td>

                <td className="px-5 py-4">
                  {offer.title}
                </td>

                <td className="px-5 py-4">
                  {offer.coupon_code||"—"}
                </td>

                <td className="px-5 py-4">
                  {offer.active
                    ?"Active"
                    :"Disabled"}
                </td>

                <td className="px-5 py-4">
                  <button
                    onClick={()=>
                      disableMutation.mutate(
                        offer.id,
                      )
                    }
                    className="rounded-xl bg-red-400/10 p-2 text-red-300"
                  >
                    <Trash2 className="size-4"/>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {open&&(
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4">
          <div className="premium-card w-full max-w-xl rounded-3xl p-7">
            <h2 className="text-2xl font-semibold">
              Add Partner Offer
            </h2>

            <select
              value={form.partner_id}
              onChange={e=>setForm({
                ...form,
                partner_id:e.target.value,
              })}
              className="mt-5 w-full rounded-2xl bg-[#0b1120] px-4 py-3"
            >
              <option value="">
                Choose partner
              </option>

              {(partnersQuery.data?.partners||[]).map(p=>(
                <option
                  key={p.id}
                  value={p.id}
                >
                  {p.name}
                </option>
              ))}
            </select>

            {[
              ["title","Offer title"],
              ["coupon_code","Coupon code"],
              ["offer_url","Offer URL"],
            ].map(([key,placeholder])=>(
              <input
                key={key}
                placeholder={placeholder}
                value={(form as any)[key]}
                onChange={e=>setForm({
                  ...form,
                  [key]:e.target.value,
                })}
                className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
              />
            ))}

            <textarea
              value={form.description}
              onChange={e=>setForm({
                ...form,
                description:e.target.value,
              })}
              placeholder="Description"
              rows={4}
              className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
            />

            <div className="mt-5 flex justify-end gap-3">
              <button
                onClick={()=>setOpen(false)}
                className="rounded-2xl border border-white/10 px-5 py-3"
              >
                Cancel
              </button>

              <button
                onClick={()=>createMutation.mutate()}
                disabled={
                  !form.partner_id||
                  !form.title||
                  createMutation.isPending
                }
                className="rounded-2xl bg-blue-500 px-5 py-3 disabled:opacity-50"
              >
                Save Offer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
