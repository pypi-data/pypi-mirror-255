"use strict";(self.webpackChunk_amzn_sagemaker_jupyter_scheduler=self.webpackChunk_amzn_sagemaker_jupyter_scheduler||[]).push([[75],{2372:(e,t,r)=>{r.r(t),r.d(t,{default:()=>$t});var n=r(6271),o=r.n(n),a=r(7363),i=r(7405);const l={ScheduleNoteBook:{MainPanel:{AdvancedOptions:{options:"Advanced Options",environmentVariables:"Environment variables",addEnvironmentvariable:"Add Variable",Key:"Key",Value:"Value",RoleArn:"Role ARN",Image:"Image",Kernel:"Kernel",securityGroup:"Security Group(s)",subnet:"Subnet(s)",s3InputFolder:"Input Folder",s3OutputFolder:"Output Folder",maxRetryAttempts:"Max retry attempts",maxRunTimeInSeconds:"Max run time (in seconds)",selectAdditionalDepency:"Select additional dependencies",efsPlaceholder:"Enter EFS file path",efsLabel:"Initialization script location (optional)",startUpScript:"Start-up script",executionEnv:"Execution enviroment",useVPC:"Use a Virtual Private Cloud (VPC) to run this job",enableEncryption:"Configure job encryption",enterKMSArnOrID:"Enter KMS key ID or ARN",ebsKey:"Job instance volume encryption KMS key",kmsKey:"Output encryption KMS key",Placeholders:{selectOrAdd:"select or add",No:"No",Add:"Add",NoneSelected:"None selected",SelectPrivateSubnets:"Select private subnet(s)",NoPrivateSubnets:"No private subnet(s) available",ImagePlaceHolder:"accountId.dkr.ecr.Region.amazonaws.com/repository[:tag] or [@digest]",KernelPlaceHolder:"kernel name",RolePlaceHolder:"arn:aws:iam::YourAccountID:role/YourRole",S3BucketPlaceHolder:"s3://bucket/path-to-your-data/"}},ErrorMessages:{JobEnvironment:{KernelImageExistError:"Image must be selected"},AdvancedOptions:{ImageError:"Image cannot be empty.",KernelError:"Kernel cannot be empty.",EFSFilePathError:"File path is not valid.",RoleArnLengthError:"Role ARN must have minimum length of 20 and maximum length of 2048.",RoleArnFormatError:"Role ARN is not properly formatted.",S3LengthError:"S3 Path must contain characters.",S3FormatError:"Invalid S3 Path format.",SecurityGroupMinError:"At least one Security Group must be selected when Subnet is selected.",SecurityGroupsMaxError:"Can only have a maximum of 5 Security Groups.",SecurityGroupSGError:"Security Group must start with sg-.",SecurityGroupLengthError:"Security Group must be less than 32 characters.",SecurityGroupFormatError:"Security Group has invalid format.",SubnetMinError:"At least one Subnet must be selected when Security Group is selected.",SubnetsMaxError:"Can only have maximum of 16 subnets.",SubnetLengthError:"Subnet must be less than 32 characters.",SubnetsFormatError:"One or more subnets has invalid format.",EnvironmentVariableEmptyError:"Key or Value cannot be empty.",EnvironmentVariableLengthError:"Key or Value cannot be more than 512 characters.",EnvironmentVariableFormatError:"Key or Value has invalid format.",KMSKeyError:"KMS key has invalid format.",MaxRetryAttemptsError:"Invalid max retry attempts must have a minimum value of 1 and a maximum value of 30.",MaxRunTimeInSecondsError:"Invalid max run time must have a minimum value of 1."},VPCErrors:{RequiresPrivateSubnet:"Running notebook jobs in a VPC requires the virtual network to use a private subnet.",NoPrivateSubnetsInSageMakerDomain:"There are no private subnets associated with your SageMaker Studio domain",YouMayChooseOtherSubnets:"You may choose to run the job using other private subnets associated with this VPC"}},Tooltips:{ImageTooltipText:"Enter the ECR registry path of the Docker image that contains the required Kernel & Libraries to execute the notebook. sagemaker-base-python-38 is selected by default",KernelTooltipText:"Enter the display name of kernel to execute the given notebook. This kernel should be installed in the above image.",LCCScriptTooltipText:"Select a lifecycle configuration script that will be run on image start-up.",VPCTooltip:"Configure the virtual network to run this job in a Virtual Private Cloud (VPC).",KMSTooltip:"Configure the cryptographic keys used to encrypt files in the job.",RoleArnTooltip:"Enter the IAM Role ARN with appropriate permissions needed to execute the notebook. By default Role name with prefix SagemakerJupyterScheduler is selected",SecurityGroupsTooltip:"Specify or add security group(s) of the desired VPC.",SubnetTooltip:"Specify or add Private subnet(s) of the desired VPC.",InputFolderTooltip:"Enter the S3 location to store the input artifacts like notebook and script.",OutputFolderTooltip:"Enter the S3 location to store the output artifacts.",InitialScriptTooltip:"Enter the file path of a local script to run before the notebook execution.",EnvironmentVariablesTooltip:"Enter key-value pairs that will be accessible in your notebook.",kmsKeyTooltip:"If you want Amazon SageMaker to encrypt the output of your notebook job using your own AWS KMS encryption key instead of the default S3 service key, provide its ID or ARN",ebsKeyTooltip:"Encrypt data on the storage volume attached to the compute instance that runs the scheduled job.",LearnMore:"Learn more",MaxRetryAttempts:"Enter a minimum value of 1 and a maximum value of 30.",MaxRunTimeInSeconds:"Enter a minimum value of 1."},StudioTooltips:{ImageTooltipText:"Select available SageMaker image.",KernelTooltipText:"Select available SageMaker Kernel.",RoleArnTooltip:"Specify a role with permission to create a notebook job.",SecurityGroupsTooltip:"Specify or add security group(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.",SubnetTooltip:"Specify or add subnet(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.",InputFolderTooltip:"Enter the S3 location where the input folder it is located.",OutputFolderTooltip:"Enter the S3 location where the output folder it is located.",InitialScriptTooltip:"Enter the EFS file path where a local script or a lifecycle configuration script is located."}}},ImageSelector:{label:"Image"},KernelSelector:{label:"Kernel",imageSelectorOption:{linkText:"More Info"}},Dialog:{awsCredentialsError:{title:"You’re not authenticated to your AWS account.",body:{text:["You haven’t provided AWS security keys or they expired. Authenticate to your AWS account with valid security keys before creating a notebook job.","Note that you must have an AWS account configured with a proper role to create notebook jobs. See %{schedulerInformation} for instructions."],links:{schedulerInformation:{linkString:"Notebook Scheduler information",linkHref:"https://docs.aws.amazon.com/sagemaker/latest/dg/notebook-auto-run.html"}}},buttons:{goToIamConsole:"Go to IAM console",enterKeysInTerminal:"Run `aws configure` in Terminal"}}}},s={expiredToken:"ExpiredToken",invalidClientTokenId:"InvalidClientTokenId",noCredentials:"NoCredentials"},u="terminal:create-new";var c,d=r(5185),m=r(3626),p=r(6516),v=r(1396),b=r(6247);!function(e){e.PublicInternetOnly="PublicInternetOnly",e.VpcOnly="VpcOnly"}(c||(c={}));var g,h,f=r(9849),y=r(9208),E=r(1982);!function(e){e[e.Large=0]="Large",e[e.Medium=1]="Medium",e[e.Small=2]="Small"}(g||(g={})),function(e){e.Filled="filled"}(h||(h={}));const S={[g.Large]:"var(--jp-content-line-height-3)",[g.Medium]:"var(--jp-content-line-height-2)",[g.Small]:"var(--jp-content-line-height-1-25)"},_={[g.Large]:"1em",[g.Medium]:"0.5em",[g.Small]:"0.25em"},k=e=>E.css`
  root: {
    background: 'var(--jp-input-active-background)',
    borderTopLeftRadius: 'var(--jp-border-radius)',
    borderTopRightRadius: 'var(--jp-border-radius)',
    fontSize: 'var(--jp-ui-font-size2)',
    '&.Mui-focused': {
      background: 'var(--jp-input-active-background)',
    },
    '&.Mui-disabled': {
      borderRadius: 'var(--jp-border-radius)',
      color: 'var(--text-input-font-color-disabled)',
    },
    '&.MuiInput-underline.Mui-disabled:before': {
      borderBottom: 'none',
    },
  },
  underline: {
    borderBottom: 'none',
    '&:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:not(.Mui-disabled):hover:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:hover:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
  },
  input: {
    color: 'var(--jp-ui-font-color0)',
    lineHeight: ${S[e]},
    padding: ${_[e]},
  },   
`,j=(E.css`
  root: {
    fontFamily: 'var(--jp-cell-prompt-font-family)',
    color: 'var(--jp-input-border-color)',
    marginBottom: 'var(--padding-small)',
    '&.Mui-error': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
  },
`,({classes:e,className:t,InputProps:r,FormHelperTextProps:n,size:a=g.Medium,variant:i,...l})=>{var s,u,c;const d=(0,E.cx)(E.css`
  .MuiFormHelperText-root.Mui-error::before {
    display: inline-block;
    vertical-align: middle;
    background-size: 1rem 1rem;
    height: var(--text-input-error-icon-height);
    width: var(--text-input-error-icon-width);
    background-image: var(--text-input-helper-text-alert-icon);
    background-repeat: no-repeat;
    content: ' ';
  }
`,t,null==e?void 0:e.root);return o().createElement(f.TextField,{"data-testid":"inputField",classes:{root:d,...e},variant:i,role:"textField",InputProps:{...r,classes:{root:(0,E.cx)(k(a),null===(s=null==r?void 0:r.classes)||void 0===s?void 0:s.root),input:(0,E.cx)(k(a),null===(u=null==r?void 0:r.classes)||void 0===u?void 0:u.input)}},FormHelperTextProps:{...n,classes:{root:(0,E.cx)(E.css`
    fontSize: 'var(--jp-ui-font-size0)',
    color: 'var(--text-input-helper-text)',
    '&.Mui-error': {
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      color: 'var(--jp-error-color1)',
    },
`,null===(c=null==n?void 0:n.classes)||void 0===c?void 0:c.root)}},...l})});var x,w=r(4129);!function(e){e.TopStart="top-start",e.Top="top",e.TopEnd="top-end",e.RightStart="right-start",e.Right="right",e.RightEnd="right-end",e.BottomStart="bottom-start",e.Bottom="bottom",e.BottomEnd="bottom-end",e.LeftStart="left-start",e.Left="left",e.LeftEnd="left-end"}(x||(x={}));const M=({children:e,classes:t,className:r,placement:n=x.Right,...a})=>{const i=(0,E.cx)(r,E.css`
  popper: {
    '& .MuiTooltip-tooltip': {
      backgroundColor: 'var(--color-light)',
      boxShadow: 'var(--tooltip-shadow)',
      color: 'var(--tooltip-text-color',
      padding: 'var(--padding-16)',
      fontSize: 'var(--font-size-0)',
    },
  },
`,null==t?void 0:t.popper);return o().createElement(w.Z,{...a,arrow:!0,classes:{popper:i,tooltip:E.css`
  tooltip: {
    '& .MuiTooltip-arrow': {
      color: 'var(--tooltip-surface)',
      '&:before': {
        boxShadow: 'var(--tooltip-shadow)',
      },
    },
  },
`},placement:n,"data-testid":"toolTip"},e)},P=E.css`
  display: flex;
  flex-direction: column;
`,C=E.css`
  display: flex;
  flex-direction: column;
`,T=E.css`
  display: inline-flex;
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(-2px);
  }
`,O=E.css`
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(1px);
  }
`,I=(e=!1)=>E.css`
  display: flex;
  flex-direction: column;
  ${e?"":"max-width : 500px;"}
  .MuiCheckbox-colorPrimary.Mui-checked {
    color: var(--jp-brand-color1);
  }
  .MuiButton-containedPrimary:hover {
    background-color: var(--jp-brand-color1);
  }
`,N=E.css`
  font-size: var(--jp-content-font-size1);
`,F=E.css`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 0.5rem;
  svg {
    width: var(--jp-ui-font-size1);
    height: var(--jp-ui-font-size1);
    path {
      fill: var(--jp-error-color1);
    }
  }
`,J=(e=!1)=>E.css`
  color: var(--jp-color-root-light-800);
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
  margin-bottom: var(--jp-ui-font-size1);
  ${e&&"\n    &:after {\n      content: '*';\n      color: var(--jp-error-color1);\n    }\n  "}
`;var D,A;!function(e){e.External="_blank",e.Content="_self"}(D||(D={})),function(e){e.None="none",e.Hover="hover",e.Always="always"}(A||(A={}));const V=({className:e,disabled:t=!1,children:r,onClick:n,target:a=D.Content,...i})=>{const l=a===D.External,s={...i,className:(0,E.cx)(E.css`
  cursor: pointer;
  text-decoration: none;
  color: var(--jp-brand-color1);

  &:hover {
    text-decoration: none;
    color: var(--jp-brand-color1);
  }
`,e),target:a,onClick:t?void 0:n,rel:l?"noopener noreferrer":void 0};return o().createElement(f.Link,{...s,"data-testid":"link"},r)};r(78);const R=e=>"string"==typeof e&&e.length>0;var L=r(5505),$=r.n(L);function z(e){try{if(!$()(e)||0===e.length)return{kernel:null,arnEnvironment:null,version:null};const t=e.split("__SAGEMAKER_INTERNAL__"),[r,n]=t,o=n&&n.split("/"),a=o&&o[0]+"/"+o[1],i=3===o.length?o[2]:null;return{kernel:r,arnEnvironment:i?`${a}/${i}`:a,version:i}}catch(e){return{kernel:null,arnEnvironment:null,version:null}}}const K=({labelInfo:e,required:t,toolTipText:r,errorMessage:n,...a})=>o().createElement("div",{className:C},o().createElement("div",{className:T},o().createElement("label",{className:J(t)}," ",e," "),r&&!a.readOnly&&o().createElement(M,{title:r,className:O},o().createElement(y.Z,null))),o().createElement(j,{...a,error:R(n),helperText:n,InputProps:{readOnly:a.readOnly,...a.InputProps}}));var B=r(6433);E.css`
  box-sizing: border-box;
  width: 100%;
  padding: var(--jp-padding-large);
  flex-direction: column;
  display: flex;
  color: var(--jp-ui-font-color0);
`,E.css`
  width: 100%;
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  padding-bottom: var(--jp-padding-20);
  color: var(--jp-ui-font-color0);
`,E.css`
  max-width: 525px;
  color: var(--jp-ui-font-color2);
  margin-bottom: var(--jp-padding-medium);
`,E.css`
  display: block;
  margin-bottom: 0.5em;
  overflow-y: scroll;
`,E.css`
  align-items: center;
  display: inline-flex;
  margin-bottom: var(--jp-padding-16);
  margin-left: 1em;
  font-size: var(--jp-ui-font-size3);
  color: var(--jp-ui-font-color0);
`;const G=E.css`
  display: flex;
  flex-direction: column;
  font-size: 12px;
  color: var(--jp-ui-font-color0);
  padding: 10px;
  overflow-x: auto;
  overflow-y: hidden;
  gap: 20px;
`,q=(E.css`
  display: flex;
  justify-content: space-between;
`,E.css`
  display: flex;
  align-items: center;
`,E.css`
  margin-bottom: var(--jp-padding-medium);
`,E.css`
  width: 50% !important;
  text-align: center;
  height: 30px;
  font-size: 12px !important;
`,E.css`
  display: inline-flex;
  justify-content: right;
`,E.css`
  height: fit-content;
  width: 90px;
  text-align: center;
  margin-right: var(--jp-padding-medium);
`,E.css`
  position: absolute;
  right: 0%;
  bottom: 0%;
  margin-bottom: var(--jp-padding-large);
`,E.css`
  div:nth-child(2) {
    width: 98%;
  }
`,E.css`
  div:nth-child(2) {
    width: 49%;
  }
`,E.css`
  div:nth-child(2) {
    width: 150px;
  }
`,E.css`
  width: 500px;
  margin-bottom: var(--jp-size-4);
`),Z=E.css`
  display: flex;
  align-items: center;
`,H=E.css`
  display: flex;
  align-items: center;
`,U=E.css`
  color: var(--jp-brand-color3);
`,Y=E.css`
  padding: 4px;
`,W=E.css`
  color: var(--jp-ui-font-color0);
`,Q=E.css`
  display: flex;
  flex-direction: column;
  gap: var(--jp-ui-font-size1);
`,X=E.css`
  color: var(--jp-error-color1);
  padding: 12px;
`,ee=l.ScheduleNoteBook.MainPanel.ErrorMessages.VPCErrors,te=l.ScheduleNoteBook.MainPanel.AdvancedOptions,re=l.ScheduleNoteBook.MainPanel.Tooltips,ne=o().createElement("div",null,o().createElement("span",{className:H}," ",re.VPCTooltip," "),o().createElement(V,{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html",target:D.External},o().createElement("p",{className:U},l.ScheduleNoteBook.MainPanel.Tooltips.LearnMore))),oe=({isChecked:e,formState:t,formErrors:r,initialSecurityGroups:n,initialSubnets:a,availableSubnets:i,setFormErrors:l,setChecked:s,setFormState:u,...c})=>o().createElement("div",{className:Z},o().createElement(B.Z,{name:"vpc-check-box",className:Y,color:"primary",checked:e,onChange:e=>{const o=e.target.checked;if(s(o),o){if(u({...t,vpc_security_group_ids:n,vpc_subnets:a}),0===a.length&&i.length>0)return void l({...r,subnetError:`${ee.RequiresPrivateSubnet} ${ee.NoPrivateSubnetsInSageMakerDomain}. ${ee.YouMayChooseOtherSubnets}`});0===i.length&&l({...r,subnetError:`${ee.RequiresPrivateSubnet} ${ee.NoPrivateSubnetsInSageMakerDomain}`})}else u({...t,vpc_security_group_ids:[],vpc_subnets:[]}),l({...r,subnetError:"",securityGroupError:""})},...c}),o().createElement("label",null,te.useVPC),o().createElement(M,{classes:{popperInteractive:W},title:ne},o().createElement(y.Z,{fontSize:"small"})));var ae=r(9419),ie=r(2679),le=r(4085);const se=E.css`
  display: flex;
  align-items: flex-end;
  padding-right: 1em;
  gap: 20px;
`,ue=E.css`
  display: flex;
  flex-direction: column;
`,ce=E.css`
  width: 170px;
`,de=(E.css`
  display: flex;
  flex-direction: column;
  margin-bottom: var(--jp-padding-large);
`,E.css`
  display: flex;
  flex-direction: column;
  gap: 16px;
`),me=E.css`
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
`,pe=E.css`
  background-color: var(--jp-brand-color1);
  font-size: var(--jp-ui-font-size1);
  text-transform: none;
`,ve=E.css`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  svg {
    width: 0.75em;
    height: 0.75em;
  }
`,be=new RegExp("[a-zA-Z_][a-zA-Z0-9_]*"),ge=new RegExp("[\\S\\s]*"),he=l.ScheduleNoteBook.MainPanel.ErrorMessages.AdvancedOptions,fe=l.ScheduleNoteBook.MainPanel.AdvancedOptions,ye=({isDisabled:e,environmentParameters:t,setEnvironmentParameters:r,index:n,formErrors:a,setFormErrors:i})=>{const l=t[n],s=e=>{const n=e.currentTarget.name,o=e.target.value,[a,i]=n.split("-"),l="envKey"===a?{key:o,value:t[i].value}:{key:t[i].key,value:o},s=[...t];s.splice(i,1,l),r(s)},u=()=>{const{key:e,value:t}=l;e.length<1||t.length<1?i({...a,environmentVariablesError:he.EnvironmentVariableEmptyError}):e.length>512||t.length>512?i({...a,environmentVariablesError:he.EnvironmentVariableLengthError}):be.test(e)&&ge.test(t)?i({...a,environmentVariablesError:""}):i({...a,environmentVariablesError:he.EnvironmentVariableFormatError})};return o().createElement("div",{className:se},o().createElement(K,{className:ce,readOnly:e,name:`envKey-${n}`,labelInfo:fe.Key,value:t[n].key,onChange:s,onBlur:u}),o().createElement(K,{className:ce,readOnly:e,name:`envValue-${n}`,labelInfo:fe.Value,value:t[n].value,onChange:s,onBlur:u}),o().createElement("div",null,!e&&o().createElement(le.Z,{onClick:()=>{(e=>{const n=[...t];n.splice(e,1),r(n),i({...a,environmentVariablesError:""})})(n),i({...a,environmentVariablesError:""})},size:"large"},o().createElement(ie.Z,null))))},Ee=l.ScheduleNoteBook.MainPanel.AdvancedOptions,Se=l.ScheduleNoteBook.MainPanel.Tooltips,_e=({allFieldsDisabled:e,isButtonDisabled:t,environmentVariables:r,setEnvironmentVariables:n,formErrors:a,...i})=>{const l=!!a.environmentVariablesError,s=o().createElement("div",{className:F},o().createElement(ae.Z,{severity:"error"},a.environmentVariablesError));return o().createElement("div",{className:de},o().createElement("div",{className:ve},o().createElement("label",{className:me},Ee.environmentVariables),e?null:o().createElement(M,{title:Se.EnvironmentVariablesTooltip},o().createElement(y.Z,null))),e&&0===r.length?o().createElement("div",{className:ue},o().createElement(j,{InputProps:{readOnly:!0},placeholder:Ee.Placeholders.NoneSelected})):o().createElement(o().Fragment,null,r.map(((t,l)=>o().createElement(ye,{isDisabled:e,key:l,environmentParameters:r,setEnvironmentParameters:n,index:l,formErrors:a,...i})))),l&&o().createElement("div",null,s),!e&&o().createElement("div",null,o().createElement(f.Button,{disabled:t,className:pe,variant:"contained",color:"primary",size:"small",onClick:()=>{n([...r,{key:"",value:""}])}},Ee.addEnvironmentvariable)))};var ke=r(8992),je=r(7338),xe=r(1360);const we=(0,ke.D)(),Me=({label:e,required:t,errorMessage:r,disabled:n,renderInput:a,tooltip:i,disabledTooltip:l,freeSolo:s,options:u,...c})=>{var d,m;null!=a||(a=t=>o().createElement(xe.Z,{...t,variant:"outlined",size:"small",margin:"dense",placeholder:e}));const p=n?l?o().createElement(M,{title:l,className:O},o().createElement(y.Z,null)):o().createElement(o().Fragment,null):i?o().createElement(M,{title:i,className:O},o().createElement(y.Z,null)):o().createElement(o().Fragment,null),v=r?o().createElement("div",{className:F},o().createElement(ae.Z,{severity:"error"},r)):o().createElement(o().Fragment,null);return o().createElement("div",{className:P},o().createElement("div",{className:T},o().createElement("label",{className:J(t)},e),p),o().createElement(je.Z,{...c,multiple:!0,renderInput:a,freeSolo:s,readOnly:n,options:u,filterOptions:(e,t)=>{const r=we(e,t);return""===t.inputValue||e.includes(t.inputValue)||r.push(t.inputValue),r},renderOption:(e,t,r)=>(u.includes(t)||(t=`Add "${t}"`),o().createElement("li",{...e},t)),componentsProps:{...c.componentsProps,popupIndicator:{...null===(d=c.componentsProps)||void 0===d?void 0:d.popupIndicator,size:"small"},clearIndicator:{...null===(m=c.componentsProps)||void 0===m?void 0:m.clearIndicator,size:"small"}}}),v)},Pe=new RegExp("^(https|s3)://([^/]+)/?(.*)$"),Ce=new RegExp("[-0-9a-zA-Z]+"),Te=new RegExp("^arn:aws[a-z\\-]*:iam::\\d{12}:role/?[a-zA-Z_0-9+=,.@\\-_/]+$"),Oe=new RegExp("^arn:aws:kms:\\w+(?:-\\w+)+:\\d{12}:key\\/[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$"),Ie=new RegExp("^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$"),Ne=l.ScheduleNoteBook.MainPanel.ErrorMessages,Fe=Ne.VPCErrors,Je=e=>e.length<20||e.length>2048?Ne.AdvancedOptions.RoleArnLengthError:Te.test(e)?"":Ne.AdvancedOptions.RoleArnFormatError,De=e=>0===e.trim().length?Ne.AdvancedOptions.S3LengthError:Pe.test(e)?"":Ne.AdvancedOptions.S3FormatError,Ae=e=>0===e.length||Oe.test(e)||Ie.test(e)?"":Ne.AdvancedOptions.KMSKeyError;var Ve;!function(e){e.LocalJL="local-jupyter-lab",e.JupyterLab="jupyterlab",e.Studio="studio"}(Ve||(Ve={}));class Re{get isStudio(){return this.type===Ve.Studio}get isLocalJL(){return this.type===Ve.LocalJL}get isJupyterLab(){return this.type===Ve.JupyterLab}get isStudioOrJupyterLab(){return this.isStudio||this.isJupyterLab}constructor(e){this.type=e}}const Le=(0,n.createContext)(void 0);function $e({app:e,children:t}){const[r,a]=(0,n.useState)((()=>function(e){return e.hasPlugin("@amzn/sagemaker-ui:project")?new Re(Ve.Studio):e.hasPlugin("@amzn/sagemaker-jupyterlab-extensions:sessionmanagement")?new Re(Ve.JupyterLab):new Re(Ve.LocalJL)}(e))),i={pluginEnvironment:r,setPluginEnvironment:a};return o().createElement(Le.Provider,{value:i},t)}function ze(){const e=(0,n.useContext)(Le);if(void 0===e)throw new Error("usePluginEnvironment must be used within a PluginEnvironmentProvider");return e}var Ke=r(2346),Be=r(3274),Ge=r(8102);const qe=l.ScheduleNoteBook.MainPanel.AdvancedOptions,Ze=l.ScheduleNoteBook.MainPanel.Tooltips,He=l.ScheduleNoteBook.MainPanel.StudioTooltips,Ue=l.ScheduleNoteBook.MainPanel.ErrorMessages,Ye=o().createElement("div",null,o().createElement("span",{className:H},Ze.kmsKeyTooltip),o().createElement(V,{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html",target:D.External},o().createElement("p",{className:U},Ze.LearnMore))),We=o().createElement("div",null,o().createElement("span",{className:H},Ze.LCCScriptTooltipText),o().createElement(V,{href:"https://aws.amazon.com/blogs/machine-learning/customize-amazon-sagemaker-studio-using-lifecycle-configurations/",target:D.External},o().createElement("p",{className:U},Ze.LearnMore))),Qe=({isDisabled:e,formState:t,formErrors:r,environmentVariables:a,setEnvironmentVariables:i,lccOptions:l,availableSecurityGroups:s,availableSubnets:u,initialSubnets:c,initialSecurityGroups:d,isVPCDomain:m,requestClient:p,enableVPCSetting:g,userDefaultValues:h,setFormState:E,handleChange:S,handleNumberValueChange:_,setSubnets:k,setSecurityGroups:j,onSelectLCCScript:x,setFormValidationErrors:w,setEnableVPCSetting:P,setRoleArn:C})=>{const{pluginEnvironment:T}=ze(),[O,I]=(0,n.useState)(!1),[N,F]=(0,n.useState)(!1),J=e=>{const t=e.target.name,n=De(e.target.value);w({...r,["s3_input"===t?"s3InputFolderError":"s3OutputFolderError"]:n})},D=e=>{const t=e.target.name,n=Ae(e.target.value);w({...r,["sm_output_kms_key"===t?"outputKMSError":"ebsKMSError"]:n})};return o().createElement("div",{className:G},o().createElement(K,{"aria-label":"role_arn",name:"role_arn",disabled:N,readOnly:e,required:!0,labelInfo:qe.RoleArn,errorMessage:r.roleError,placeholder:qe.Placeholders.RolePlaceHolder,onChange:S,value:t.role_arn,onBlur:e=>{const{value:t}=e.target,n=Je(t);C(t),w({...r,roleError:n})},toolTipText:T.isStudioOrJupyterLab?He.RoleArnTooltip:Ze.RoleArnTooltip}),o().createElement(K,{name:"s3_input",onChange:S,required:!0,disabled:N,readOnly:e,value:t.s3_input,placeholder:qe.Placeholders.S3BucketPlaceHolder,labelInfo:qe.s3InputFolder,errorMessage:r.s3InputFolderError,onBlur:J,toolTipText:T.isStudioOrJupyterLab?He.InputFolderTooltip:Ze.InputFolderTooltip}),o().createElement(K,{name:"s3_output",onChange:S,required:!0,disabled:N,readOnly:e,value:t.s3_output,placeholder:qe.Placeholders.S3BucketPlaceHolder,labelInfo:qe.s3OutputFolder,errorMessage:r.s3OutputFolderError,onBlur:J,toolTipText:T.isStudioOrJupyterLab?He.OutputFolderTooltip:Ze.OutputFolderTooltip}),!e&&o().createElement("div",{className:Z},o().createElement(f.Checkbox,{"data-testid":"kms_checkbox",name:"kms_checkbox",className:Y,color:"primary",checked:O,onChange:e=>{const n=e.target.checked;I(n);const o=n?h.sm_output_kms_key:"",a=n?h.sm_volume_kms_key:"";E({...t,sm_output_kms_key:o,sm_volume_kms_key:a}),w({...r,outputKMSError:Ae(o),ebsKMSError:Ae(a)})}}),o().createElement("label",null,qe.enableEncryption),o().createElement(M,{classes:{popperInteractive:W},title:Ye},o().createElement(y.Z,{fontSize:"small"}))),(e||O)&&o().createElement(o().Fragment,null,o().createElement(K,{name:"sm_output_kms_key",onChange:S,required:!1,readOnly:e,disabled:N,value:t.sm_output_kms_key,placeholder:e?qe.Placeholders.NoneSelected:qe.enterKMSArnOrID,labelInfo:qe.kmsKey,errorMessage:r.outputKMSError,onBlur:D,toolTipText:e?void 0:Ze.kmsKeyTooltip}),o().createElement(K,{name:"sm_volume_kms_key",onChange:S,required:!1,readOnly:e,disabled:N,value:t.sm_volume_kms_key,placeholder:e?qe.Placeholders.NoneSelected:qe.enterKMSArnOrID,labelInfo:qe.ebsKey,errorMessage:r.ebsKMSError,onBlur:D,toolTipText:e?void 0:Ze.ebsKeyTooltip})),m&&!e&&o().createElement(oe,{isChecked:g,setChecked:P,initialSecurityGroups:d,initialSubnets:c,availableSubnets:u,formState:t,formErrors:r,setFormErrors:w,setFormState:E,"data-testid":"vpc-checkbox"}),(m&&g||e)&&o().createElement(o().Fragment,null,o().createElement(Me,{required:!0,name:"vpc_subnets",disabled:e||T.isStudioOrJupyterLab&&0===u.length,label:qe.subnet,options:u,value:t.vpc_subnets,onChange:(e,n,o)=>{const[a,i]=((e,t)=>{if(0===e.length)return 0===t.length?["",""]:[Ne.AdvancedOptions.SubnetMinError,void 0];if(e&&e.length>0){if(e.length>16)return[Ne.AdvancedOptions.SubnetsMaxError,void 0];for(const t of e){if(t.length>32)return[Ne.AdvancedOptions.SubnetLengthError,void 0];if(!Ce.test(t))return[Ne.AdvancedOptions.SubnetsFormatError,void 0]}if(0===t.length)return["",Ne.AdvancedOptions.SecurityGroupMinError]}return["",void 0]})(n,t.vpc_security_group_ids);k(n),w({...r,securityGroupError:null!=i?i:r.securityGroupError,subnetError:null!=a?a:""})},errorMessage:r.subnetError,placeholder:`${qe.Placeholders.SelectPrivateSubnets}`,tooltip:T.isStudio?He.SubnetTooltip:Ze.SubnetTooltip,disabledTooltip:`${qe.Placeholders.NoPrivateSubnets}`,freeSolo:!0}),o().createElement(Me,{required:!0,className:"securityGroupSelector",name:"vpc_security_group_ids",disabled:e||T.isStudioOrJupyterLab&&0===s.length,label:qe.securityGroup,options:s,value:t.vpc_security_group_ids,onChange:(e,n,o)=>{const[a,i]=((e,t)=>{if(0===e.length)return 0===t.length?["",""]:[Ne.AdvancedOptions.SecurityGroupMinError,void 0];if(e.length>0){if(e.length>5)return[Ne.AdvancedOptions.SecurityGroupsMaxError,void 0];for(const t of e){if(!t.startsWith("sg-"))return[Ne.AdvancedOptions.SecurityGroupSGError,void 0];if(t.length>32)return[Ne.AdvancedOptions.SecurityGroupLengthError,void 0];if(!Ce.test(t))return[Ne.AdvancedOptions.SecurityGroupFormatError,void 0]}if(0===t.length)return["",Ne.AdvancedOptions.SubnetMinError]}return["",void 0]})(n,t.vpc_subnets);j(n),w({...r,securityGroupError:null!=a?a:"",subnetError:null!=i?i:r.subnetError})},errorMessage:r.securityGroupError,placeholder:`${qe.Placeholders.selectOrAdd} ${qe.securityGroup}`,tooltip:T.isStudio?He.SecurityGroupsTooltip:Ze.SecurityGroupsTooltip,disabledTooltip:`${qe.Placeholders.No} ${qe.securityGroup}`,freeSolo:!0})),T.isStudioOrJupyterLab&&o().createElement("div",{className:Q},o().createElement(Ge.Z,{id:"startup-script-select-label"},qe.startUpScript,o().createElement(M,{title:We},o().createElement(y.Z,{fontSize:"small"}))),o().createElement(Ke.Z,{labelId:"startup-script-select-label",id:"startup-script-select",disabled:N,readOnly:e,value:t.sm_lcc_init_script_arn,onChange:e=>x(e.target.value)},l&&l.map((e=>o().createElement(Be.Z,{key:e,value:e},e))))),o().createElement(_e,{isButtonDisabled:e||a.length>=48||!!r.environmentVariablesError,allFieldsDisabled:e,environmentVariables:a,setEnvironmentVariables:i,formErrors:r,setFormErrors:w}),o().createElement("div",null,o().createElement(K,{placeholder:e?qe.Placeholders.NoneSelected:qe.efsPlaceholder,labelInfo:qe.efsLabel,required:!1,value:t.sm_init_script,name:"sm_init_script",readOnly:e,disabled:N,errorMessage:r.efsFilePathError,onChange:S,onBlur:e=>{const t=e.target.value;0===t.trim().length?w({...r,efsFilePathError:""}):(async e=>{const t=v.URLExt.join(p.baseUrl,"/validate_volume_path");F(!0);const n=await b.ServerConnection.makeRequest(t,{method:"POST",body:JSON.stringify({file_path:e})},p);F(!1),200!==n.status||!0===(await n.json()).file_path_exist?w({...r,efsFilePathError:""}):w({...r,efsFilePathError:Ue.AdvancedOptions.EFSFilePathError})})(t)},toolTipText:e?void 0:T.isStudio?He.InitialScriptTooltip:Ze.InitialScriptTooltip})),o().createElement(K,{name:"max_retry_attempts",type:"number",onChange:_,required:!0,disabled:N,readOnly:e,value:t.max_retry_attempts,placeholder:qe.maxRetryAttempts,labelInfo:qe.maxRetryAttempts,errorMessage:r.maxRetryAttemptsError,onBlur:e=>{const t=(e=>{const t=parseInt(e);return isNaN(t)||t<0||t>30?Ne.AdvancedOptions.MaxRetryAttemptsError:""})(e.target.value);w({...r,maxRetryAttemptsError:t})},toolTipText:Ze.MaxRetryAttempts}),o().createElement(K,{name:"max_run_time_in_seconds",type:"number",onChange:_,required:!0,disabled:N,readOnly:e,value:t.max_run_time_in_seconds,placeholder:qe.maxRunTimeInSeconds,labelInfo:qe.maxRunTimeInSeconds,errorMessage:r.maxRunTimeInSecondsError,onBlur:e=>{const t=(e=>{const t=parseInt(e);return isNaN(t)||t<0?Ne.AdvancedOptions.MaxRunTimeInSecondsError:""})(e.target.value);w({...r,maxRunTimeInSecondsError:t})},toolTipText:Ze.MaxRunTimeInSeconds}))},Xe="No script",et=new Set(["sm_kernel","sm_image","sm_lcc_init_script_arn","role_arn","vpc_security_group_ids","vpc_subnets","s3_input","s3_output","sm_init_script","sm_output_kms_key","sm_volume_kms_key","max_run_time_in_seconds","max_retry_attempts"]),tt=(e,t,r,n)=>{var o,a;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e[n]?e[n].split(","):[]}else if(r===i.JobsView.CreateForm){if(e&&n in e){const t=e[n];return t?t.split(","):[]}const r=null===(o=null==t?void 0:t.find((e=>e.name===n)))||void 0===o?void 0:o.value;return(null===(a=null==r?void 0:r.filter((e=>e.is_selected)))||void 0===a?void 0:a.map((e=>e.name)))||[]}return[]},rt=(e,t,r,n)=>{var o;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e[n]}else if(r===i.JobsView.CreateForm)return e&&n in e?e[n]:(null===(o=null==t?void 0:t.find((e=>e.name===n)))||void 0===o?void 0:o.value)||"";return""},nt=(e,t,r,n)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e[n]}else if(t===i.JobsView.CreateForm&&e&&n in e)return e[n];return r},ot=(e,t,r)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e[r]}else if(t===i.JobsView.CreateForm&&e&&r in e)return e[r];return""},at=({label:e,value:t,options:r,onChange:n,freeSolo:a,customListItemRender:i,renderInput:l,...s})=>{var u;const c=Object.fromEntries(r.map((e=>[e.value,e])));let d=t;return!a&&"string"==typeof t&&t in c&&(d=c[t]),o().createElement(o().Fragment,null,o().createElement(je.Z,{...s,id:`${e}-selectinput`,renderOption:(e,t,r)=>o().createElement("li",{...e},i?i(t,t.label,r.selected):t.label),componentsProps:{...s.componentsProps,popupIndicator:{...null===(u=s.componentsProps)||void 0===u?void 0:u.popupIndicator,size:"small"}},options:r,onChange:(e,t,r)=>{(t&&"string"!=typeof t||a)&&n&&n(t||"")},value:d,renderInput:l||(e=>o().createElement(xe.Z,{...e,variant:"outlined",size:"small",margin:"dense"}))}))},it=({label:e,required:t=!0,toolTipText:r,toolTipArea:n,errorMessage:a,...i})=>{const l=n&&o().createElement("div",null,o().createElement("span",{className:H},n.descriptionText),n.toolTipComponent);return o().createElement("div",{className:P},o().createElement("div",{className:T},o().createElement("label",{className:J(t)},e),(r||n)&&!i.readOnly&&o().createElement(M,{title:l||r||"",className:O,disableInteractive:null===n},o().createElement(y.Z,null))),o().createElement(at,{label:e,disableClearable:!0,...i}))},lt=E.css`
  display: flex;
  flex-direction: column;
  padding: 10px;
`,st=E.css`
  display: flex;
  flex-direction: column;
  gap: 20px;
`,ut=E.css`
  display: flex;
  flex-direction: column;
`,ct=(E.css`
  transform: rotate(90deg);
`,E.css`
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`),dt=E.css`
  font-size: var(--jp-ui-font-size0);
  min-width: max-content;
`,mt=E.css`
  font-size: var(--jp-ui-font-size0);
  color: var(--jp-inverse-layout-color4);
  padding-right: 5px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
`,pt=E.css`
  width: 100%;
`,vt=E.css`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  &[data-selected='true'] {
    background-image: var(--jp-check-icon);
    background-size: 15px;
    background-repeat: no-repeat;
    background-position: 100% center;
  }
  & > p {
    max-width: calc(100% - 10px);
  }
`,bt=(e,t,r)=>o().createElement("span",{className:pt},o().createElement("div",{className:vt,"data-selected":r},o().createElement("p",null,t||e.label)),gt(e.optionMetadata&&e.optionMetadata.description)),gt=e=>{if(!e)return;const t=e.match(/(((https?:\/\/)|(www\.))[^\s]+)/g);if(t){console.log("links",t);for(const r of t)e=e.replace(r," ")}const r=e.trim();return o().createElement("div",{className:ct},o().createElement("span",{className:mt},r),t&&t.map((e=>o().createElement(V,{className:dt,key:e,href:e,target:D.External},l.KernelSelector.imageSelectorOption.linkText))))};r(9850);const ht=["datascience-1.0","sagemaker-data-science-38","1.8.1-cpu-py36","pytorch-1.8-gpu-py36","sagemaker-sparkmagic","tensorflow-2.6-cpu-py38-ubuntu20.04-v1","tensorflow-2.6-gpu-py38-cu112-ubuntu20.04-v1","sagemaker-sparkanalytics-v1"];var ft;async function yt(e,t){if(e.endsWith(".ipynb"))try{return(await t.get(e)).content.metadata.kernelspec.name}catch(e){return""}return""}!function(e){e.Custom="customImage",e.Sagemaker="smeImage",e.Session="session"}(ft||(ft={}));const Et={smeImage:"Sagemaker Image",customImage:"Custom Image",prefered:"Use image from preferred session",session:"Use image from other session"};function St(e,t,r){const n=Object.values(e).filter((e=>{const n=e.arnEnvironment.split("/")[1];return r?(null==e?void 0:e.group)===t&&ht.includes(n):((null==e?void 0:e.group)!==ft.Sagemaker||!e.label.includes("Geospatial"))&&(null==e?void 0:e.group)===t}));return{label:Et[t],value:"",options:n.map((e=>({label:e.label,value:t===ft.Session?e.label:e.arnEnvironment,group:Et[t],optionMetadata:e,options:e.versionOptions})))}}const _t=l.ScheduleNoteBook.MainPanel.Tooltips,kt=l.ScheduleNoteBook.MainPanel.StudioTooltips,jt=({isDisabled:e,formState:t,formErrors:r,setFormState:a,setFormErrors:s,model:u,jobsView:c,requestClient:d,contentsManager:m})=>{var p,g;const{pluginEnvironment:h}=ze(),[f,y]=(0,n.useState)({arnEnvironment:null,kernel:null,version:null}),[E,S]=(0,n.useState)({});(0,n.useEffect)((()=>{(async function(e){const t=v.URLExt.join(e.baseUrl,"api/kernelspecs"),r=await b.ServerConnection.makeRequest(t,{},e);if(200===r.status)return await r.json()})(d).then((async e=>{var t;e&&S(function(e){const t={},r=e.kernelspecs;return Object.values(r).forEach((e=>{var r;if(!e)return;const n=(null===(r=e.spec)||void 0===r?void 0:r.metadata)?e.spec.metadata.sme_metadata:null,{imageName:o,kernelName:a}=function(e){try{if(!$()(e)||0===e.length)return{imageName:null,kernelName:null};const[t,r]=e.split("(");return{imageName:r&&r.slice(0,-1).split("/")[0],kernelName:t&&t.slice(0,-1)}}catch(e){return{imageName:null,kernelName:null}}}(e.spec.display_name),{kernel:i,arnEnvironment:l,version:s}=z(e.name);if(!(i&&l&&o&&a))return;const u={arnEnvironment:l,kernelOptions:[{label:a,value:i}],versionOptions:s?[{label:`v${s}`,value:s}]:void 0,label:s?`${o} v${s}`:o,description:(null==n?void 0:n.description)?n.description:void 0,group:n&&n.is_template?ft.Sagemaker:ft.Custom};if(t[l]){const{kernelOptions:e}=t[l];if(!e.some((e=>e.value===i))){const r=[...e,{label:a,value:i}];t[l].kernelOptions=r}if(s){const{versionOptions:e}=t[l];if(!e.some((e=>e.value===s))){const r={label:`v${s}`,value:s.toString()},n=Array.isArray(e)?[...e,r]:[r];t[l].versionOptions=n}}}else t[l]=u})),t}(e));const r=await yt(u.inputFile,m),n=r in(null!==(t=null==e?void 0:e.kernelspecs)&&void 0!==t?t:{})?r:"",o=((e,t,r)=>{if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}return{kernel:null,arnEnvironment:null,version:null}}if(r===i.JobsView.CreateForm){if(e&&"sm_image"in e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}return z(t)||{kernel:null,arnEnvironment:null,version:null}}return z(t)||{kernel:null,arnEnvironment:null,version:null}})(u.runtimeEnvironmentParameters,n,c);y(o),a((e=>({...e,sm_kernel:o.kernel||"",sm_image:o.arnEnvironment||""})))}))}),[]);const _=[...null!==(p=St(E,ft.Sagemaker,!1).options)&&void 0!==p?p:[],...null!==(g=St(E,ft.Custom).options)&&void 0!==g?g:[]],k=(0,n.useMemo)((()=>{var e;return f.arnEnvironment&&(null===(e=E[f.arnEnvironment])||void 0===e?void 0:e.kernelOptions)||[]}),[E,f]),j=!!r.jobEnvironmentError,x=o().createElement("div",{className:F},o().createElement(ae.Z,{severity:"error"},r.jobEnvironmentError));return(0,n.useEffect)((()=>{f.arnEnvironment&&f.kernel&&r.jobEnvironmentError&&s({...r,jobEnvironmentError:""})}),[f.arnEnvironment,f.kernel]),0===Object.keys(E).length?null:o().createElement("div",{className:lt},o().createElement("div",{className:st},o().createElement("div",{className:ut},o().createElement(it,{"data-testid":"sm_image_dropdown",options:_,value:f.arnEnvironment,label:l.ImageSelector.label,customListItemRender:bt,onChange:(e,r)=>{var n;if(!e||"string"==typeof e)return;const o=(null===(n=e.optionMetadata)||void 0===n?void 0:n.kernelOptions)||[],i=o.length>0?o[0].value:null,l=r?r.value:null;a({...t,sm_image:e.value+(l?"/"+l:""),sm_kernel:null!=i?i:""}),y({arnEnvironment:e.value,kernel:i,version:l})},readOnly:e,groupBy:e=>{var t;return null!==(t=e.group)&&void 0!==t?t:""},toolTipText:h.isStudio?kt.ImageTooltipText:_t.ImageTooltipText}),r.jobEnvironmentError&&o().createElement("div",{className:N},j&&x)),o().createElement(it,{options:k,value:f.kernel,label:l.KernelSelector.label,onChange:e=>{e&&"string"!=typeof e&&e&&(a({...t,sm_kernel:e.value}),y({...f,kernel:e.value}))},readOnly:e,toolTipText:h.isStudio?kt.KernelTooltipText:_t.KernelTooltipText})))},xt=l.ScheduleNoteBook.MainPanel.AdvancedOptions,wt=l.ScheduleNoteBook.MainPanel.Tooltips,Mt=({setFormState:e,formState:t,isDisabled:r,formErrors:a,setFormErrors:i,model:l,executionEnvironments:s})=>{const u=(0,n.useMemo)((()=>((e,t)=>{var r,n;if(e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}const o=null===(r=null==t?void 0:t.find((e=>"image"===e.name)))||void 0===r?void 0:r.value,a=null===(n=null==t?void 0:t.find((e=>"kernel"===e.name)))||void 0===n?void 0:n.value;return R(o)&&R(a)?z(`${a}__SAGEMAKER_INTERNAL__${o}`):{kernel:null,arnEnvironment:null,version:null}})(l.runtimeEnvironmentParameters,null==s?void 0:s.auto_detected_config)),[]);(0,n.useEffect)((()=>{e({...t,sm_kernel:u.kernel||"",sm_image:u.arnEnvironment||""})}),[u]);const c=r=>{const n=r.target.name,o=r.target.value;e({...t,[n]:o})};return o().createElement("div",{className:G},o().createElement(K,{name:"sm_image",onChange:c,readOnly:r,required:!0,value:t.sm_image,placeholder:xt.Placeholders.ImagePlaceHolder,labelInfo:xt.Image,errorMessage:a.ImageError,onBlur:e=>{const{value:t}=e.target,r=t.length<=0?Ne.AdvancedOptions.ImageError:"";i({...a,ImageError:r})},toolTipText:wt.ImageTooltipText}),o().createElement(K,{name:"sm_kernel",onChange:c,readOnly:r,required:!0,value:t.sm_kernel,placeholder:xt.Placeholders.KernelPlaceHolder,labelInfo:xt.Kernel,errorMessage:a.KernelError,onBlur:e=>{const{value:t}=e.target,r=t.length<=0?Ne.AdvancedOptions.KernelError:"";i({...a,KernelError:r})},toolTipText:wt.KernelTooltipText}))},Pt=l.ScheduleNoteBook.MainPanel.Tooltips,Ct=({setFormState:e,formState:t,isDisabled:r,formErrors:a,setFormErrors:i,contentsManager:s,model:u})=>{const[c,d]=(0,n.useState)([]),[m,p]=(0,n.useState)([]),g=async()=>{const e=b.ServerConnection.makeSettings(),t=v.URLExt.join(e.baseUrl,"/sagemaker_images"),r=await b.ServerConnection.makeRequest(t,{},e);return 200==r.status?(await r.json()).map((e=>({label:e.image_display_name,value:e.image_arn}))):[]},h=async()=>{const e=b.ServerConnection.makeSettings(),t=v.URLExt.join(e.baseUrl,"/api/kernelspecs"),r=await b.ServerConnection.makeRequest(t,{},e);let n=null;const o=[],a=[];if(200===r.status){const e=await r.json();n=e.default,e.kernelspecs&&Object.values(e.kernelspecs).forEach((e=>{if(e){o.push(e.name);let t=e.name;e.spec&&(t=e.spec.display_name),a.push({label:t,value:e.name})}}))}return{defaultKernelName:n,kernelNames:o,kernelOptions:a}};return(0,n.useEffect)((()=>{Promise.all([yt(u.inputFile,s),g(),h()]).then((r=>{const n=r[0],o=r[1],a=r[2];let i=null,l=null;o&&o.length>0&&d(o),u.runtimeEnvironmentParameters&&u.runtimeEnvironmentParameters.sm_image?i=u.runtimeEnvironmentParameters.sm_image:o&&o.length>0&&(i=o[0].value),a&&a.kernelOptions&&a.kernelOptions.length>0&&p(a.kernelOptions),l=u.runtimeEnvironmentParameters&&u.runtimeEnvironmentParameters.sm_kernel?u.runtimeEnvironmentParameters.sm_kernel:a.kernelNames.indexOf(n)>=0?n:a.defaultKernelName||"",e({...t,sm_image:i,sm_kernel:l})})).catch((e=>console.error(e)))}),[]),o().createElement("div",{className:G},o().createElement(it,{"data-testid":"sm_image_dropdown",options:c,value:t.sm_image,label:l.ImageSelector.label,onChange:r=>{r&&"string"!=typeof r&&e({...t,sm_image:r.value})},readOnly:r,toolTipText:Pt.ImageTooltipText,required:!0}),o().createElement(it,{"data-testid":"sm_kernel_dropdown",options:m,value:t.sm_kernel,label:l.KernelSelector.label,onChange:r=>{r&&"string"!=typeof r&&e({...t,sm_kernel:r.value})},readOnly:r,toolTipText:Pt.KernelTooltipText,required:!0}))},Tt=e=>{const{pluginEnvironment:t}=ze();return o().createElement(o().Fragment,null,t.isStudio&&o().createElement(jt,{...e}),t.isJupyterLab&&o().createElement(Ct,{...e}),t.isLocalJL&&o().createElement(Mt,{...e}))},Ot=e=>{const{executionEnvironments:t,settingRegistry:r,jobsView:a,requestClient:l,errors:s,handleErrorsChange:u,model:d,handleModelChange:m}=e,p=(0,n.useMemo)((()=>{return e=null==t?void 0:t.auto_detected_config,a===i.JobsView.CreateForm&&(null===(r=null==e?void 0:e.find((e=>"app_network_access_type"===e.name)))||void 0===r?void 0:r.value)||"";var e,r}),[]),v=(0,n.useMemo)((()=>{var e,r;const n=[],o=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"lcc_arn"===e.name)))||void 0===r?void 0:r.value)||[];n.push(Xe),n.push(...o);const l=(s=d.runtimeEnvironmentParameters,((u=a)===i.JobsView.JobDetail||u===i.JobsView.JobDefinitionDetail)&&s&&s.sm_lcc_init_script_arn||Xe);var s,u;return d.runtimeEnvironmentParameters&&l!==Xe&&n.push(l),{allLCCOptions:n,selectedLccValue:l}}),[]),b=(0,n.useMemo)((()=>((e,t,r)=>{var n;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e.role_arn}else if(r===i.JobsView.CreateForm){if(e&&"role_arn"in e)return e.role_arn;const r=null===(n=null==t?void 0:t.find((e=>"role_arn"===e.name)))||void 0===n?void 0:n.value;if((null==r?void 0:r.length)>0)return r[0]}return""})(d.runtimeEnvironmentParameters,t.auto_detected_config,a)),[]),g=(0,n.useMemo)((()=>rt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"s3_output")),[]),h=(0,n.useMemo)((()=>rt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"s3_input")),[]),f=(0,n.useMemo)((()=>nt(d.runtimeEnvironmentParameters,a,1,"max_retry_attempts")),[]),y=(0,n.useMemo)((()=>nt(d.runtimeEnvironmentParameters,a,172800,"max_run_time_in_seconds")),[]),E=(0,n.useMemo)((()=>{var e,r;const n=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"vpc_security_group_ids"===e.name)))||void 0===r?void 0:r.value)||[];return null==n?void 0:n.map((e=>e.name))}),[]),S=(0,n.useMemo)((()=>{var e,r;const n=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"vpc_subnets"===e.name)))||void 0===r?void 0:r.value)||[];return null==n?void 0:n.map((e=>e.name))}),[]),_=(0,n.useMemo)((()=>p===c.PublicInternetOnly?{securityGroups:[],subnets:[]}:{securityGroups:0===S.length&&a===i.JobsView.CreateForm?[]:tt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"vpc_security_group_ids"),subnets:tt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"vpc_subnets")}),[]),k=(0,n.useMemo)((()=>((e,t)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e.sm_init_script}else if(t===i.JobsView.CreateForm&&e&&"sm_init_script"in e)return e.sm_init_script;return""})(d.runtimeEnvironmentParameters,a)),[]),j=(0,n.useMemo)((()=>(e=>{const t=[];if(e)for(const r in e)if(!et.has(r)){const n={key:r,value:e[r]};t.push(n)}return t})(d.runtimeEnvironmentParameters)),[]),x=(0,n.useMemo)((()=>ot(d.runtimeEnvironmentParameters,a,"sm_output_kms_key")),[]),w=(0,n.useMemo)((()=>ot(d.runtimeEnvironmentParameters,a,"sm_volume_kms_key")),[]),M=(0,n.useMemo)((()=>{if(p===c.PublicInternetOnly)return!1;const e=_.subnets;return 0!==S.length&&(0===e.length&&S.length,!0)}),[]),[P,C]=(0,n.useState)({sm_lcc_init_script_arn:v.selectedLccValue||"",role_arn:b||"",vpc_security_group_ids:_.securityGroups||"",vpc_subnets:_.subnets||"",s3_input:h||"",s3_output:g||"",sm_kernel:"",sm_image:"",sm_init_script:k||"",sm_output_kms_key:x||"",sm_volume_kms_key:w||"",max_retry_attempts:f,max_run_time_in_seconds:y}),[T,O]=(0,n.useState)({...P,sm_output_kms_key:"",sm_volume_kms_key:""});(0,n.useEffect)((()=>{const e=(e=>e&&0===e.length?`${Fe.RequiresPrivateSubnet} ${Fe.NoPrivateSubnetsInSageMakerDomain}`:"")(S),t=(r=_.subnets)&&0===r.length?`${Fe.RequiresPrivateSubnet} ${Fe.NoPrivateSubnetsInSageMakerDomain}. ${Fe.YouMayChooseOtherSubnets}`:"";var r;u({...s,roleError:Je(b),s3InputFolderError:De(h),s3OutputFolderError:De(g),environmentsStillLoading:"",kernelsStillLoading:"",subnetError:M&&(e||t)||""})}),[]);const[N,F]=(0,n.useState)();(0,n.useEffect)((()=>{(async function(e){return(await e.get("@amzn/sagemaker-jupyter-scheduler:advanced-options","advancedOptions")).composite})(r).then((e=>{F(e)}))}),[]),(0,n.useEffect)((()=>{var e,t,r,n,o;let a={},i={},l={};const c=null!==(e=null==N?void 0:N.role_arn)&&void 0!==e?e:"";c&&c!==b&&(a={...a,role_arn:c},i={...i,roleError:Je(c)});const d=null!==(t=null==N?void 0:N.s3_input)&&void 0!==t?t:"";d&&d!==h&&(a={...a,s3_input:d},i={...i,s3InputFolderError:De(d)});const m=null!==(r=null==N?void 0:N.s3_output)&&void 0!==r?r:"";m&&m!==g&&(a={...a,s3_output:m},i={...i,s3OutputFolderError:De(m)});const p=null!==(n=null==N?void 0:N.sm_output_kms_key)&&void 0!==n?n:"";p&&p!==x&&(l={...l,sm_output_kms_key:p});const v=null!==(o=null==N?void 0:N.sm_volume_kms_key)&&void 0!==o?o:"";v&&v!==w&&(l={...l,sm_volume_kms_key:v}),l={...a,...l},Object.keys(a).length>0&&O({...T,...a}),Object.keys(l).length>0&&C({...P,...l}),Object.keys(i).length>0&&u({...s,...i})}),[N]);const[J,D]=(0,n.useState)(j),[A,V]=(0,n.useState)(M),R=(0,n.useMemo)((()=>{const e={};return null==J||J.map((t=>{const{key:r,value:n}=t;0!==r.trim().length&&0!==n.trim().length&&(e[r]=n)})),e}),[J]);(0,n.useEffect)((()=>{var e,t;const r=(null===(e=T.vpc_security_group_ids)||void 0===e?void 0:e.join(","))||"",n=(null===(t=T.vpc_subnets)||void 0===t?void 0:t.join(","))||"";m({...d,runtimeEnvironmentParameters:{...T,vpc_security_group_ids:r,vpc_subnets:n,...R}})}),[T,R]);const L=a===i.JobsView.JobDefinitionDetail||a===i.JobsView.JobDetail;return o().createElement("div",{className:I(L)},o().createElement(Tt,{isDisabled:L,formState:T,setFormState:O,formErrors:s,setFormErrors:u,...e}),o().createElement(Qe,{isDisabled:L,formState:T,setFormState:O,handleChange:e=>{const t=e.target.name,r=e.target.value;O({...T,[t]:r})},handleNumberValueChange:e=>{const t=e.target.name,r=parseInt(e.target.value);O({...T,[t]:isNaN(r)?"":r})},requestClient:l,formErrors:s,setFormValidationErrors:u,environmentVariables:J,userDefaultValues:P,setEnvironmentVariables:D,lccOptions:v.allLCCOptions,availableSecurityGroups:E,availableSubnets:S,initialSecurityGroups:_.securityGroups,initialSubnets:_.subnets,setSubnets:e=>{O({...T,vpc_subnets:e})},setRoleArn:e=>{O({...T,role_arn:e})},setSecurityGroups:e=>{O({...T,vpc_security_group_ids:e})},onSelectLCCScript:e=>{O({...T,sm_lcc_init_script_arn:e})},isVPCDomain:p===c.VpcOnly,enableVPCSetting:A,setEnableVPCSetting:V}))};var It=r(2453);function Nt(e){return getComputedStyle(document.body).getPropertyValue(e).trim()}function Ft(){const e=document.body.getAttribute("data-jp-theme-light");return(0,It.Z)({spacing:4,components:{MuiButton:{defaultProps:{size:"small"}},MuiFilledInput:{defaultProps:{margin:"dense"}},MuiFormControl:{defaultProps:{margin:"dense",size:"small"}},MuiFormHelperText:{defaultProps:{margin:"dense"}},MuiIconButton:{defaultProps:{size:"small"}},MuiInputBase:{defaultProps:{margin:"dense",size:"small"}},MuiInputLabel:{defaultProps:{margin:"dense"},styleOverrides:{root:{display:"flex",alignItems:"center",color:"var(--jp-ui-font-color0)",gap:"6px"}}},MuiListItem:{defaultProps:{dense:!0}},MuiOutlinedInput:{defaultProps:{margin:"dense"}},MuiFab:{defaultProps:{size:"small"}},MuiAutocomplete:{defaultProps:{componentsProps:{paper:{elevation:4}}}},MuiTable:{defaultProps:{size:"small"}},MuiTextField:{defaultProps:{margin:"dense",size:"small"}},MuiToolbar:{defaultProps:{variant:"dense"}}},palette:{background:{paper:Nt("--jp-layout-color1"),default:Nt("--jp-layout-color1")},mode:"true"===e?"light":"dark",primary:{main:Nt("--jp-brand-color1"),light:Nt("--jp-brand-color2"),dark:Nt("--jp-brand-color0")},error:{main:Nt("--jp-error-color1"),light:Nt("--jp-error-color2"),dark:Nt("--jp-error-color0")},warning:{main:Nt("--jp-warn-color1"),light:Nt("--jp-warn-color2"),dark:Nt("--jp-warn-color0")},success:{main:Nt("--jp-success-color1"),light:Nt("--jp-success-color2"),dark:Nt("--jp-success-color0")},text:{primary:Nt("--jp-ui-font-color1"),secondary:Nt("--jp-ui-font-color2"),disabled:Nt("--jp-ui-font-color3")}},shape:{borderRadius:2},typography:{fontFamily:Nt("--jp-ui-font-family"),fontSize:12,htmlFontSize:16,button:{textTransform:"capitalize"}}})}const Jt=({requestClient:e,contentsManager:t,commands:r,jobsView:a,errors:c,handleErrorsChange:g,...h})=>{const{pluginEnvironment:f}=ze(),[y,E]=(0,n.useState)("");(0,n.useEffect)((()=>{const t={...c,environmentsStillLoading:"EnvironmentsStillLoadingError",kernelsStillLoading:"KernelsStillLoadingError"};g(t),a===i.JobsView.CreateForm?(async()=>{const t=v.URLExt.join(e.baseUrl,"/advanced_environments"),n=await b.ServerConnection.makeRequest(t,{},e);if(200!==n.status&&f.isLocalJL){const e=(await n.json()).error_code;throw Object.values(s).indexOf(e)>=0&&(async e=>{const t=o().createElement(o().Fragment,null,l.Dialog.awsCredentialsError.body.text.map(((e,t)=>o().createElement("p",{key:t,className:q},((e,t)=>{const r=e.split("%");return o().createElement(o().Fragment,null,r.map((e=>{if(e.startsWith("{")){const[r,...n]=e.replace("{","").split("}"),a=t[r],i=n.join("");return a?o().createElement(o().Fragment,null,o().createElement(V,{key:r,href:a.linkHref,target:D.External},a.linkString),i):o().createElement(o().Fragment,null,e)}return o().createElement(o().Fragment,null,e)})))})(e,l.Dialog.awsCredentialsError.body.links))))),r=new d.Dialog({title:l.Dialog.awsCredentialsError.title,body:t,buttons:[d.Dialog.cancelButton(),d.Dialog.okButton({label:l.Dialog.awsCredentialsError.buttons.enterKeysInTerminal})]});(await r.launch()).button.label===l.Dialog.awsCredentialsError.buttons.enterKeysInTerminal&&e.execute(u)})(r),new Error(n.statusText)}return await n.json()})().then((async e=>{j(!1),_(e)})).catch((e=>{E(e.message)})):j(!1)}),[a,h.model.inputFile]);const[S,_]=(0,n.useState)({}),[k,j]=(0,n.useState)(!0);return y?o().createElement("div",{className:X},y):k?null:a!==i.JobsView.CreateForm||(null==S?void 0:S.auto_detected_config)?o().createElement(m.Z,{theme:Ft()},o().createElement(p.StyledEngineProvider,{injectFirst:!0},o().createElement(Ot,{executionEnvironments:S,requestClient:e,contentsManager:t,jobsView:a,errors:c,handleErrorsChange:g,...h}))):null},Dt={id:"@amzn/sagemaker-scheduler:scheduler",autoStart:!1,requires:[a.ISettingRegistry],provides:i.Scheduler.IAdvancedOptions,activate:(e,t)=>r=>{const n=e.serviceManager.serverSettings,a=new b.ContentsManager;return o().createElement(f.StyledEngineProvider,{injectFirst:!0},o().createElement($e,{app:e},o().createElement(Jt,{requestClient:n,contentsManager:a,settingRegistry:t,commands:e.commands,...r})))}};var At;!function(e){e.eventDetail="eventDetail"}(At||(At={}));const Vt="NotebookJobs",Rt={"org.jupyter.jupyter-scheduler.notebook-header.create-job":`${Vt}-CreateJob-FromNotebookHeader`,"org.jupyter.jupyter-scheduler.file-browser.create-job":`${Vt}-CreateJob-FromFileBrowser`,"org.jupyter.jupyter-scheduler.launcher.show-jobs":`${Vt}-JobsList-OpenFromLauncher`,"org.jupyter.jupyter-scheduler.create-job.create-job":`${Vt}-CreateJob-Create`,"org.jupyter.jupyter-scheduler.create-job.cancel":`${Vt}-CreateJob-Cancel`,"org.jupyter.jupyter-scheduler.create-job.create-job.success":`${Vt}-CreateJob-Success`,"org.jupyter.jupyter-scheduler.create-job.create-job.failure":`${Vt}-CreateJob-Failure`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition":`${Vt}-CreateJob-CreateJobDefinition`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition.success":`${Vt}-CreateJobDefinition-Success`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition.failure":`${Vt}-CreateJobDefinition-Failure`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job":`${Vt}-CreateJobFromDefinition-Create`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.success":`${Vt}-CreateJobFromDefinition-Success`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.failure":`${Vt}-CreateJobFromDefinition-Failure`,"org.jupyter.jupyter-scheduler.create-job-from-definition.cancel":`${Vt}-CreateJobFromDefinition-Cancel`,"org.jupyter.jupyter-scheduler.create-job.job-type.run-now":`${Vt}-CreateJobType-RunNow`,"org.jupyter.jupyter-scheduler.create-job.job-type.run-on-schedule":`${Vt}-CreateJobType-RunOnSchedule`,"org.jupyter.jupyter-scheduler.create-job.advanced-options.expand":`${Vt}-CreateJob-ExpandAdvancedOptions`,"org.jupyter.jupyter-scheduler.create-job.advanced-options.collapse":`${Vt}-CreateJob-CollapseAdvancedOptions`,"org.jupyter.jupyter-scheduler.jobs-list.reload":`${Vt}-JobsList-Reload`,"org.jupyter.jupyter-scheduler.jobs-definition-list.reload":`${Vt}-JobsDefinitionList-Reload`,"org.jupyter.jupyter-scheduler.jobs-list.open-input-file":`${Vt}-JobsList-OpenInputFile`,"org.jupyter.jupyter-scheduler.jobs-list.open-output-file":`${Vt}-JobsList-OpenOutputFile`,"org.jupyter.jupyter-scheduler.job-list.stop-confirm":`${Vt}-JobsList-StopConfirm`,"org.jupyter.jupyter-scheduler.jobs-list.download":`${Vt}-JobsList-Download`,"org.jupyter.jupyter-scheduler.jobs-list.open-detail":`${Vt}-JobsList-OpenDetail`,"org.jupyter.jupyter-scheduler.jobs-list.delete":`${Vt}-JobsList-Delete`,"org.jupyter.jupyter-scheduler.jobs-list.stop":`${Vt}-JobsList-Stop`,"org.jupyter.jupyter-scheduler.job-definition-list.open-detail":`${Vt}-JobsDefinitionList-OpenDetail`,"org.jupyter.jupyter-scheduler.job-definition-list.pause":`${Vt}-JobsDefinitionList-Pause`,"org.jupyter.jupyter-scheduler.job-definition-list.resume":`${Vt}-JobsDefinitionList-Resume`,"org.jupyter.jupyter-scheduler.job-definition-list.delete":`${Vt}-JobsDefinitionList-Delete`,"org.jupyter.jupyter-scheduler.job-detail.open-input-file":`${Vt}-JobsDefinitionList-OpenInputFile`,"org.jupyter.jupyter-scheduler.job-detail.open-output-file":`${Vt}-JobsDefinitionList-OpenOutputFile`,"org.jupyter.jupyter-scheduler.job-detail.delete":`${Vt}-JobDetail-Delete`,"org.jupyter.jupyter-scheduler.job-detail.stop":`${Vt}-JobDetail-Stop`,"org.jupyter.jupyter-scheduler.job-detail.download":`${Vt}-JobDetail-Download`,"org.jupyter.jupyter-scheduler.job-detail.reload":`${Vt}-JobDetail-Reload`,"org.jupyter.jupyter-scheduler.job-definition-detail.reload":`${Vt}-JobDefinitonDetail-Reload`,"org.jupyter.jupyter-scheduler.job-definition-detail.run":`${Vt}-JobDefinitonDetail-Run`,"org.jupyter.jupyter-scheduler.job-definition-detail.pause":`${Vt}-JobDefinitonDetail-Pause`,"org.jupyter.jupyter-scheduler.job-definition-detail.resume":`${Vt}-JobDefinitonDetail-Resume`,"org.jupyter.jupyter-scheduler.job-definition-detail.edit":`${Vt}-JobDefinitonDetail-Edit`,"org.jupyter.jupyter-scheduler.job-definition-detail.delete":`${Vt}-JobDefinitonDetail-Delete`,"org.jupyter.jupyter-scheduler.job-definition-edit.save":`${Vt}-JobDefinitonDetail-Save`,"org.jupyter.jupyter-scheduler.job-definition-edit.cancel":`${Vt}-JobDefinitonEdit-Cancel`},Lt=async e=>{var t;let r;const n=null!==(t=Rt[e.body.name])&&void 0!==t?t:e.body.name;r=e.body.detail?JSON.stringify({name:n,error:e.body.detail}):n,window&&window.panorama&&window.panorama("trackCustomEvent",{eventType:At.eventDetail,eventDetail:r,eventContext:Vt,timestamp:e.timestamp.getTime()})},$t=[Dt,{id:"@amzn/sagemaker-scheduler:schedulerTelemetry",autoStart:!0,provides:i.Scheduler.TelemetryHandler,activate:e=>Lt}]}}]);