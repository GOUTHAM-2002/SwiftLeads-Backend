"""
CREATE TABLE IF NOT EXISTS settings (  
    id UUID PRIMARY KEY,  

    -- API Keys  
    vapi_api_key TEXT,  
    assistant_id TEXT,  
    phone_number_id TEXT,  

    -- Model Settings  
    model TEXT DEFAULT 'gpt-4o',  
    provider TEXT DEFAULT 'openai',  
    first_message TEXT DEFAULT 'Hello, is that {first_name}?',  
    system_prompt TEXT,  

    -- Voice Settings  
    voice_id TEXT DEFAULT 'aTxZrSrp47xsP6Ot4Kgd',  
    voice_provider TEXT DEFAULT '11labs',  
    stability NUMERIC(3,2) DEFAULT 0.5,  
    similarity_boost NUMERIC(3,2) DEFAULT 0.75,  
    voice_filler_injection_enabled BOOLEAN DEFAULT FALSE,  
    backchanneling_enabled BOOLEAN DEFAULT FALSE,  
    background_denoising_enabled BOOLEAN DEFAULT FALSE,  

    -- Phone Numbers (JSON to store multiple phone numbers)  
    phone_numbers JSONB,  

    -- Timestamps  
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP  
);  
"""

"""
CREATE TABLE PhoneNumbers (  
    id SERIAL PRIMARY KEY,  
    user_id UUID NOT NULL REFERENCES settings(id) ON DELETE CASCADE,  
    phone_number_id VARCHAR(255) NOT NULL UNIQUE,   
    phone_number VARCHAR(15) NOT NULL UNIQUE,  
    status VARCHAR(10) NOT NULL CHECK (status IN ('ACTIVE', 'INACTIVE')),  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    name VARCHAR(255) NOT NULL  
);
"""
"""
CREATE TABLE campaign_contact_info (  
        -- Unique Identifier  
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 

        user_id UUID NOT NULL REFERENCES settings(id) ON DELETE CASCADE,
        campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, 

        -- Contact Information (Required Fields)  
        phone TEXT NOT NULL,  
        name TEXT NOT NULL,  
        email TEXT,  
        
        -- Business Information  
        company TEXT,  
        business_name TEXT,  
        title TEXT,  
        website TEXT,  
        linkedin TEXT,  
        source TEXT,  

        -- Location Details  
        timezone TEXT,  
        address TEXT,  
        city TEXT,  
        state TEXT,  
        zip_code TEXT,  
        country TEXT,  

        -- Sales Pipeline Information  
        pipeline_stage TEXT,  
        status TEXT,  

        -- Timestamps  
        created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
        last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
        
        -- Notes  
        notes TEXT,  

        -- Call Tracking  
        last_called TIMESTAMP WITH TIME ZONE,  
        total_calls INTEGER DEFAULT 0,  
        successful_calls INTEGER DEFAULT 0,  
        total_call_duration INTEGER DEFAULT 0,  
        
        -- Voicemail Tracking  
        voicemail_count INTEGER DEFAULT 0,  
        last_voicemail_date TIMESTAMP WITH TIME ZONE,  
        total_voicemail_duration INTEGER DEFAULT 0,  
        
        -- Call Details  
        call_summary TEXT,  
        call_transcript TEXT,  
        success_evaluation TEXT,  
        end_reason TEXT,  
        
        -- Recording and Cost Tracking  
        recording_urls TEXT[],  
        duration_seconds INTEGER,  
        
        -- Cost Tracking  
        total_cost NUMERIC(10,5) DEFAULT 0,  
        speech_to_text_cost NUMERIC(10,5) DEFAULT 0,  
        llm_cost NUMERIC(10,5) DEFAULT 0,  
        text_to_speech_cost NUMERIC(10,5) DEFAULT 0,  
        vapi_cost NUMERIC(10,5) DEFAULT 0,  
        
        -- Lead Qualification  
        hot_lead BOOLEAN DEFAULT FALSE
        );  
"""

"""
        CREATE TABLE campaigns (  
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  
            
            user_id UUID NOT NULL REFERENCES settings(id) ON DELETE CASCADE,  
            
            name TEXT NOT NULL,  
            description TEXT NOT NULL,  
    
            call_window_start TIME WITHOUT TIME ZONE NOT NULL,  
            call_window_end TIME WITHOUT TIME ZONE NOT NULL,  
            
            
            -- Timestamps for tracking  
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
        );  
"""

"""
          CREATE TABLE contacts (  
        -- Unique Identifier  
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 

        user_id UUID REFERENCES settings(id) ON DELETE CASCADE , 

        -- Contact Information (Required Fields)  
        phone TEXT NOT NULL,  
        name TEXT NOT NULL,  
        email TEXT,  
        
        -- Business Information  
        company TEXT,  
        business_name TEXT,  
        title TEXT,  
        website TEXT,  
        linkedin TEXT,  
        source TEXT,  

        -- Location Details  
        timezone TEXT,  
        address TEXT,  
        city TEXT,  
        state TEXT,  
        zip_code TEXT,  
        country TEXT,  

        -- Sales Pipeline Information  
        pipeline_stage TEXT,  
        status TEXT,  

        -- Timestamps  
        created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
        last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
        
        -- Notes  
        notes TEXT,  

        -- Call Tracking  
        last_called TIMESTAMP WITH TIME ZONE,  
        total_calls INTEGER DEFAULT 0,  
        successful_calls INTEGER DEFAULT 0,  
        total_call_duration INTEGER DEFAULT 0,  
        
        -- Voicemail Tracking  
        voicemail_count INTEGER DEFAULT 0,  
        last_voicemail_date TIMESTAMP WITH TIME ZONE,  
        total_voicemail_duration INTEGER DEFAULT 0,  
        
        -- Call Details  
        call_summary TEXT,  
        call_transcript TEXT,  
        success_evaluation TEXT,  
        end_reason TEXT,  
        
        -- Recording and Cost Tracking  
        recording_urls TEXT[],  
        duration_seconds INTEGER,  
        
        -- Cost Tracking  
        total_cost NUMERIC(10,5) DEFAULT 0,  
        speech_to_text_cost NUMERIC(10,5) DEFAULT 0,  
        llm_cost NUMERIC(10,5) DEFAULT 0,  
        text_to_speech_cost NUMERIC(10,5) DEFAULT 0,  
        vapi_cost NUMERIC(10,5) DEFAULT 0,  
        
        -- Lead Qualification  
        hot_lead BOOLEAN DEFAULT FALSE
        );  
"""

"""
CREATE TABLE campaign_metrics (  
    -- Unique Identifier  
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  

    -- Campaign Identifier  
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,  

    -- Call Tracking  
    total_calls INTEGER DEFAULT 0,  
    voicemail_count INTEGER DEFAULT 0,  
    hot_lead BOOLEAN DEFAULT FALSE,  
    total_duration INTERVAL DEFAULT '0 seconds',  
    
    -- Cost Tracking  
    total_cost NUMERIC(10, 5) DEFAULT 0,  
    avg_cost_per_call NUMERIC(10, 5) DEFAULT 0,  
    
    -- Timestamps  
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP  
);
"""

"""

CREATE TABLE properties (  
    id SERIAL PRIMARY KEY,  
    address VARCHAR(255),  
    name VARCHAR(255),  
    company_name VARCHAR(255),  
    phone_number VARCHAR(50),  
    locality VARCHAR(255),  
    url VARCHAR(255),  
    image_url VARCHAR(255),  
    list_price NUMERIC,  
    type VARCHAR(100),  
    bedrooms INTEGER,  
    bathrooms INTEGER,  
    sq_ft INTEGER,  
    date DATE,  
    source VARCHAR(255)  
);



"""
