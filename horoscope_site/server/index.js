import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import multer from 'multer';

const app=express();
const port=process.env.PORT||8787;
const upload=multer({storage:multer.memoryStorage(),limits:{fileSize:12*1024*1024}});
app.use(cors({origin:process.env.ALLOWED_ORIGIN||true}));
app.use(express.json({limit:'1mb'}));
app.get('/health',(_,res)=>res.json({ok:true,service:'gochara-atlas'}));
const system=`You are the evidence-first research assistant for Gochara Atlas. Separate extracted observations, astronomical calculations, statistical relationships, hypotheses and unsupported claims. The project uses date-only data when birth time is absent: never invent birth time, Ascendant, houses, D1, D9 or dasha. A UTC-noon value is only a reproducible midpoint, not a birth time. Treat Moon sign/nakshatra as time-sensitive when appropriate. Do not infer wealth, marriage, children, success, failure or causation without dated sources. If a PDF or image contains a horoscope, first transcribe only what is visible, then explain uncertainty. Keep astrology as a research hypothesis, not established fact.`;
app.post('/api/chat',upload.single('attachment'),async(req,res)=>{
 try{
  if(!process.env.OPENAI_API_KEY)return res.status(500).json({error:'OPENAI_API_KEY is not configured on the server.'});
  const question=String(req.body.question||'Analyze the attachment.');const content=[{type:'input_text',text:question}];
  if(req.file){const mime=req.file.mimetype||'application/octet-stream';const data=req.file.buffer.toString('base64');if(mime.startsWith('image/'))content.push({type:'input_image',image_url:`data:${mime};base64,${data}`});else if(mime==='application/pdf')content.push({type:'input_file',filename:req.file.originalname,file_data:`data:${mime};base64,${data}`});else return res.status(400).json({error:'Only PDF, PNG, JPEG and WebP attachments are supported.'});}
  const response=await fetch('https://api.openai.com/v1/responses',{method:'POST',headers:{'Authorization':`Bearer ${process.env.OPENAI_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify({model:process.env.OPENAI_MODEL||'gpt-4.1-mini',input:[{role:'system',content:[{type:'input_text',text:system}]},{role:'user',content}],max_output_tokens:1200})});
  const data=await response.json();if(!response.ok)return res.status(response.status).json({error:data.error?.message||'OpenAI request failed'});const answer=data.output_text||data.output?.flatMap(x=>x.content||[]).map(x=>x.text||'').join('')||'No text response returned.';res.json({answer});
 }catch(e){res.status(500).json({error:e.message||'Server error'});}
});
app.listen(port,()=>console.log(`Gochara Atlas API listening on http://localhost:${port}`));
